
from data_analysis.OpeningLDA import OpeningLDA
from scraper.Scraper import * 
from scraper.Paths import Paths
import threading as th
import numpy as np 
from sklearn.metrics.pairwise import cosine_similarity
import json 

class QueryHandler: 
    
    opening_lda:OpeningLDA
    hyperparams:dict = json.load(open(Paths.HYPERPARAMS_JSON, 'r'))
    
    ''' __init__(load_from_file) - constructor

        --- PARAMETERS --- 
            load_from_file (str) - optionally specify a filename to load a pre-trained OpeningLDA model; if not specified,
                                   then this attribute must be explicitly set after initialization.
    '''
    def __init__(self, load_from_file:str=""):
         if load_from_file: self.opening_lda = OpeningLDA.load(load_from_file)
         else: self.opening_lda = None
        
    ''' handle_user_query(query) - handles a query by a user 

        --- DESCRIPTION --- 
            Takes as input the query by a user, i.e. the user's description of their playstyle, and 
            returns a dictionary (JSON object) in the correct format for the client-side to render 
            on the page. 
            
            Step 1. takes the query and tokenizes it to search the index, stores the matches in descending
            order of relevance. 
            
            Step 2. takes the query and compares it to pre-computed LDA results from all possible openings, 
            and stores these matches in descending order of relevance.
            
            Step 3. takes the resulting dictionary and orders it based on success rate 
            
            Averages the two results and returns the dictionary (JSON object) described below. 
            
        --- PARAMETERS --- 
            query (str) - the user's query (description of their playstyle) as a single string 
            
        --- RETURNS --- 
            [+] Data: application/json
                - a dictionary (JSON object) containing a single key called "messages" with the value
                as a single list of strings, where each is a description of an opening to recommend
                to the user, ordered by relevance (descending). 
            
            [+] Format: 
            
                { 
                    "messages": [
                        "Description of recommendation 1...",
                        "Description of recommendation 2...",
                        ...
                    ]
                }
        
        --- RAISES --- 
            Raises AttributeError if self.opening_lda has not been loaded or set (i.e. if it is None)
    '''
    def handle_user_query(self, query:dict[str,str], debug=False) -> dict[str,list[str]]: 
        
        # NOTE: Maybe use threading to improve the runtime ??? !!! 
        
        # Check and make sure self.opening_lda has been loaded or set 
        if self.opening_lda == None: raise AttributeError("Error in QueryHandler.handle_user_query(): OpeningLDA attribute has not been set.")
        
        query_text:str = query['message']   # User's given description of their playstyle
        query_color:str = query['color']    # Color indicated by user 
        
        # Tokenize the query 
        query_tokens:list[str] = Scraper.tokenize(query_text)
        
        # STEP 1: search the index for matches
        index_matches:list[dict[str,int]] = [self.opening_lda.index[tok] for tok in query_tokens if tok in self.opening_lda.index]
        
        # Convert index_matches to a single dict containing the matches for each opening as a single key:val pair with the relative 
        # term frequency for each code
        # i.e., sum the tfs for each opening across all index matches and then divide each sum by the number of terms in that openings descriptions
        rel_index_matches:dict[str,int] = {}    # Dict containing each opening code with the sum of all tfs across all matches for that code
        for d in index_matches:
            # k == opening code, v == tf 
            for k,v in d.items(): 
                try: rel_index_matches[k] += v              # If this code (k) exists already in the sum matches dict, then add v
                except KeyError: rel_index_matches[k] = v   # If this code (k) does not exist already in the sum matches dict, then add it

        # Convert these sums of tfs to relative tfs using the values in self.opening_lda.num_terms
        for k,v in rel_index_matches.items(): rel_index_matches[k] = v / self.opening_lda.num_terms[k]
        
        # Sort the index matches (descending order)
        rel_index_matches = dict(sorted(rel_index_matches.items(), key=lambda item: item[1], reverse=True))
        
        if debug: 
            print("\nRelative index matches:")
            for k,v in rel_index_matches.items(): print(f"{k} : {v}")
        
        # STEP 2: perform LDA on the user's query 
        lda_matched_topics = self.opening_lda.process_new_text(query_tokens)

        # Perform cosine similarity on the resulting vector (lda_matched_topics) and save in a dictionary 
        # with key:val => eco:cosine_sim(lda_matched_topics, eco_topic_matched_vector)
        cosine_sims:dict[str, float] = {}
        all_ecos = list(self.opening_lda.texts.keys())
        
        for eco,doc_vector in zip(all_ecos,self.opening_lda.topic_doc_matrix): 
            cosine_sims[eco] = cosine_similarity(
                                    np.array(lda_matched_topics).reshape(1,-1),
                                    np.array(doc_vector).reshape(1,-1)
                                )[0][0]
        
        if debug: 
            print("\nCosine similarities:")
            for k,v in cosine_sims.items(): print(f"{k} : {v}")
        
        # STEP 3: apply weights for each factor to determine the final ranking 
        #         NOTE: use hyperparameters to calculate the relative weights for index matches, cosine 
        #               similarities, and success rate
        
        # Create a dictionary for the success rates of each opening for the query_color for quicker lookups
        success_rates:dict[str,float] = {eco:d['success-rate'][query_color] for eco,d in self.opening_lda.openings.items() if d['success-rate']}
        
        # Apply the weights (hyperparams) to each factor to determine the final rankings 
        index_weight:float = self.hyperparams['weights']['index']
        cos_weight:float = self.hyperparams['weights']['cosine']
        success_weight:float = self.hyperparams['weights']['success']
        
        final_rankings:dict[str, float] = {}
        for eco in all_ecos:
            try:
                avg:float = index_weight*rel_index_matches[eco] + cos_weight*cosine_sims[eco] + success_weight*success_rates[eco] 
                if debug: 
                    print(f"\nECO: {eco}")
                    print(f"\tIndex matches[{eco}] = {rel_index_matches[eco]}")
                    print(f"\tCos sim[{eco}] = {cosine_sims[eco]}")
                    print(f"\tSuccess[{eco}] = {success_rates[eco]}")
                    print(f"\tWeighted avg = {avg}")
                final_rankings[eco] = avg
            except KeyError: continue
                
        sorted_final_rankings:dict[str, float] = dict(sorted(final_rankings.items(), key=lambda item: item[1], reverse=True))
        
        if(debug): 
            print("\nFinal rankings:")
            for k,v in sorted_final_rankings.items(): print(f"{k} : {v}")
            
        
        
    
