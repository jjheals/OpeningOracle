
from data_analysis.OpeningLDA import OpeningLDA
from scraper.Scraper import * 
from scraper.Paths import Paths
import threading as th
import numpy as np 
from sklearn.metrics.pairwise import cosine_similarity
import json 
from data_analysis.OpeningGPT import OpeningGPT

class QueryHandler: 
    
    # STATIC Attributes
    NUM_RETURN:int = 5      # The number of matches to return (i.e. return the top NUM_RETURN matches)
    
    # DYNAMIC Attributes
    opening_lda:OpeningLDA
    hyperparams:dict = json.load(open(Paths.HYPERPARAMS_JSON, 'r'))
    all_ecos:list[str] 
    opening_gpt:OpeningGPT
    
    ''' __init__(load_from_file) - constructor

        --- PARAMETERS --- 
            load_from_file (str) - optionally specify a filename to load a pre-trained OpeningLDA model; if not specified,
                                   then this attribute must be explicitly set after initialization.
    '''
    def __init__(self, load_from_file:str=""):
        if load_from_file: 
            self.opening_lda = OpeningLDA.load(load_from_file)
            self.opening_lda.__construct_topic_doc_matrix__()
            self.all_ecos = list(self.opening_lda.texts.keys())
        else: self.opening_lda = None
        
        self.opening_gpt = OpeningGPT()
        
        print("QueryHandler init DONE.")
        
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
            
            compute_final_summary (bool) - specify whether to compute a final summary from the already precomputed 
                                           summary we have for this opening. note that if set to True, then the 
                                           process will noticably take longer to return. if set to False (default), 
                                           the process will just use the precomputed summaries and will return much
                                           quicker
                                           
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
    def handle_user_query(self, query:dict[str,str], compute_final_summary:bool=False, debug=False) -> dict[str,list[str]]: 
        
        if debug: print("Handling user query...")
        
        # NOTE: Maybe use threading to improve the runtime ??? !!! 
        
        # Get the parts of the user's query
        query_text:str = query['message']   # User's given description of their playstyle
        query_color:str = query['color']    # Color indicated by user 
        
        # Check and make sure self.opening_lda has been loaded or set 
        if self.opening_lda == None: raise AttributeError("Error in QueryHandler.handle_user_query(): OpeningLDA attribute has not been set.")
        
        # Load hyperparameters
        index_weight:float = self.hyperparams['weights']['index']
        cos_weight:float = self.hyperparams['weights']['cosine']
        success_weight:float = self.hyperparams['weights']['success']
        
        # Create a dictionary for the success rates of each opening for the query_color for quicker lookups
        success_rates:dict[str,float] = {eco:d['success-rate'][query_color] for eco,d in self.opening_lda.openings.items() if d['success-rate']}
        
        # Tokenize the query 
        query_tokens:list[str] = Scraper.tokenize(query_text)
                
        # Step 1: index matches 
        rel_index_matches:dict[str,float] = self.__find_index_matches__(query_tokens, debug=debug) 
        
        # Step 2: LDA & cosine similarities 
        cosine_sims:dict[str,float] = self.__lda_cosine_sims__(query_tokens, debug=debug)

        # STEP 3: apply weights for each factor to determine the final ranking 
        #         NOTE: use hyperparameters to calculate the relative weights for index matches, cosine 
        #               similarities, and success rate
        sorted_final_rankings:dict[str,float] = self.__calc_final_ranks__(rel_index_matches, 
                                                                          cosine_sims, 
                                                                          success_rates, 
                                                                          index_weight, 
                                                                          cos_weight, 
                                                                          success_weight, 
                                                                          debug=debug)
        
        # Use these final rankings to determine which openings to run through the GPT model 
        # i.e. get the top NUM_RETURN eco codes
        sorted_eco_matches:list[str] = list(sorted_final_rankings.keys())
            
        # Get the precomputed summaries from the stored data
        all_summaries:dict[str,str] = json.load(open(Paths.SUMMARIES_JSON))
        these_summaries:dict[str,str] = {}
        
        # Iterate through the sorted_eco_matches dict and get the summaries for each eco (preserve order)
        # Get no more than NUM_RETURN summaries to return 
        count:int = 0   # Counter to check how many we have to return at a given iteration 
        
        # While we do not have NUM_RETURN summaries, keep getting more  
        while count < QueryHandler.NUM_RETURN: 
            for eco in sorted_eco_matches:
                
                # Check if we have a summary for this eco
                if eco not in all_summaries or not all_summaries[eco]: continue 
                
                these_summaries[eco] = all_summaries[eco]   # Add this eco's summary to these_summaries
                count += 1                                  # Increment the counter 
                
                if count == QueryHandler.NUM_RETURN: break
                
                continue                                    # Continue to the next highest ranked eco 
                
            # If we get here without retrieving NUM_RETURN summaries, then just break and 
            # return what we have
            break 
        
        # NOTE: just a precaution, should theoretically never happen if the summaries are all computed
        # If we found no results, then take the first element in all_summaries and just return that
        # since we don't really care what it is if we found no relevant matches (i.e., all matches are
        # irrelevant, but we want to return something, so we can just return an irrelevant one)
        if not these_summaries: 
            tmp_eco = list(all_summaries.keys())[0]
            these_summaries[tmp_eco:all_summaries[tmp_eco]]
                
        for e,s in these_summaries.items(): print(f"{e}: {s}\n") 
        
        # NOTE: include threading to generate e/a summary independently of each other ?? 
        # DO SOMETHING ... 
        
        # Run the summaries through the model to generate the final summary for each 
        if debug: print(f"QueryHandler.handle_user_query: Starting retrieving/generating summaries. \nNOTICE: compute_final_summaries is set to {compute_final_summary}.\n")
        
        for e,summ in these_summaries.items():
            if debug: print(f"Summarizing eco: {e}")
            
            this_opening_dict:dict = self.opening_lda.openings[e]
            
            # Format the string containing the links to include in the response
            formatted_links:str = "Links to data sources: " 
            for s,l in this_opening_dict['links'].items(): 
                if l: formatted_links += f"{s} [{l}], "
                
            formatted_links[:-2]    # Remove trailing ", "
            
            # Either generate the summary for this eco or use the precomputed one 
            if compute_final_summary: this_sum:str = self.opening_gpt.generate_summary(summ, temperature=0.8)
            else: this_sum:str = summ
            
            # Add this summary to the dict of summaries 
            these_summaries[e] = f"{this_opening_dict['opening-name']}, {this_opening_dict['variation-name']} ({e}): {this_sum} {formatted_links}"
            
        return {"messages": list(these_summaries.values())}
        
        
    ''' __find_index_matches__(tokens) - first step in handling a user's query. 
    
        --- DESCRIPTION --- 
            Take as input a list of tokens and search the index (contained in self.opening_lda) for matches. Convert
            the matches to relative term frequencies (i.e. term freq per document) and sort the results.
        
        --- PARAMETERS --- 

            tokens (list[str]) - list of tokens to search the index; important that the query is tokenized using the 
                                 same tokenization function as used to create the index (i.e. Scraper.tokenize()). 
        
            debug (bool) - optional - specify whether to print debug statements. default == False
            
        --- RETURNS --- 
            (dict[str,float]) A dictionary containing the ECO code and its match as a dict sorted on the values (sorted on
                              the ranks, not ECO)
            
            Return format example: 
            
                {
                    "B03" : 0.5,
                    "A00" : 0.4, 
                    "D45" : 0.3, 
                    ... 
                }
    '''
    def __find_index_matches__(self, query_tokens:list[str], debug:bool=False) -> dict[str,float]:
        
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
        
        for k,v in rel_index_matches.items(): 
            if self.opening_lda.num_terms[k] > 0: 
                rel_index_matches[k] = v / self.opening_lda.num_terms[k]
            else: 
                rel_index_matches[k] = 0
                
        # Sort the index matches (descending order)
        rel_index_matches = dict(sorted(rel_index_matches.items(), key=lambda item: item[1], reverse=True))
        
        if debug: 
            print("\nRelative index matches:")
            for k,v in rel_index_matches.items(): print(f"{k} : {v}")
            
        return rel_index_matches
    
    ''' __lda_cosine_sims__(tokens) - perform LDA on the tokens and then cosine simiarity using the documents 

        --- DESCRIPTION --- 
            Takes as input a list of tokens, presumably generated via the user's query, and then runs these tokens
            through the LDA model in self.opening_lda. After vectorizing the tokens (i.e. LDA), performs cosine 
            similarity on the resulting vector and the precomputed topic vectors for each document (opening). 
        
        --- PARAMETERS --- 
        
            tokens (list[str]) - list of tokens to vectorize; important that the query is tokenized using the 
                                 same tokenization function as used to create the index (i.e. Scraper.tokenize()). 
            
            debug (bool) - optional - specify whether to print debug statements. default == False
            
        --- RETURNS --- 
            (dict[str,float]) A dictionary containing the ECO code and its match as a dict sorted on the values (sorted on
                              the ranks, not ECO)
            
            Return format example: 
            
                {
                    "B03" : 0.5,
                    "A00" : 0.4, 
                    "D45" : 0.3, 
                    ... 
                }
    '''
    def __lda_cosine_sims__(self, query_tokens:list[str], debug:bool=False) -> dict[str,float]: 
        lda_matched_topics = self.opening_lda.process_new_text(query_tokens)

        # Perform cosine similarity on the resulting vector (lda_matched_topics) and save in a dictionary 
        # with key:val => eco:cosine_sim(lda_matched_topics, eco_topic_matched_vector)
        cosine_sims:dict[str, float] = {}
        
        
        for eco,doc_vector in zip(self.all_ecos, self.opening_lda.topic_doc_matrix): 
            cosine_sims[eco] = cosine_similarity(
                                    np.array(lda_matched_topics).reshape(1,-1),
                                    np.array(doc_vector).reshape(1,-1)
                                )[0][0]
        
        if debug: 
            print("\nCosine similarities:")
            for k,v in cosine_sims.items(): print(f"{k} : {v}")
            
        return cosine_sims
    
    ''' __calc_final_ranks__(rel_index_matches, cosine_sims, success_rates, index_weight, cos_weight, success_weight) 
    
        --- DESCRIPTION --- 
            Calculates the final rankings for the ECOs based on the given sub results (index matches, cosine sims, and success rates) 
            and taking into account the given weight of each factor. 
            
        --- PARAMETERS --- 
        
            Factors/sub results: 
                
                rel_index_matches (dict[str,float]) - dictionary of key : val -> eco : index_match_percent
                cosine_sums (dict[str,float]) - dictionary of key : val -> eco : cosine_sim
                success_rates (dict[str,float]) - dictionary of key : val -> eco : success_rate_for_color
                
            Hyperparameters: 

                index_weight (float) - the weight of the index matches on the final ranks
                cos_weight (float) - the weight of LDA & cosine similarity of an ECO to the query
                success_weight (float) - the weight of the success rate for a given ECO
            
            debug (bool) - optional - specify whether to print debug information
            
        --- RETURNS --- 
            (dict[str,float]) A sorted dictionary of key : val -> ECO : percent_matched_to_query (sorted on the val, descending)
            
            Return format example: 
            
                {
                    "B03" : 0.5,
                    "A00" : 0.4, 
                    "D45" : 0.3, 
                    ... 
                }
    '''
    def __calc_final_ranks__(self, 
                             rel_index_matches:dict[str,float], cosine_sims:dict[str,float], success_rates:dict[str,float], 
                             index_weight:float, cos_weight:float, success_weight:float, debug:bool=False
                        ) -> dict[str,float]: 
        
        # Apply the weights (hyperparams) to each factor to determine the final rankings 
        final_rankings:dict[str, float] = {}
        for eco in self.all_ecos:
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
        
        # Sort the resulting dictionary
        sorted_final_rankings:dict[str, float] = dict(sorted(final_rankings.items(), key=lambda item: item[1], reverse=True))
        
        if(debug): 
            print("\nFinal rankings:")
            for k,v in sorted_final_rankings.items(): print(f"{k} : {v}")
        
        return sorted_final_rankings
