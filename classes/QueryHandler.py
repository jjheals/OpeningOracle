
from data_analysis.OpeningLDA import OpeningLDA
from scraper.Scraper import * 

from flask import jsonify 
import threading as th

class QueryHandler: 
    
    opening_lda:OpeningLDA
    
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
    def handle_user_query(self, query:dict[str,str]) -> dict[str,list[str]]: 
        
        # NOTE: Maybe use threading to improve the runtime ??? !!! 
        
        # Check and make sure self.opening_lda has been loaded or set 
        if self.opening_lda == None: raise AttributeError("Error in QueryHandler.handle_user_query(): OpeningLDA attribute has not been set.")
        
        # Tokenize the query 
        query_tokens:list[str] = Scraper.tokenize(query)
        
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
        
        print("Rel index matches:\n") 
        for k,v in rel_index_matches.items(): print(f"{k} : {v}")
        
                
                    
        # STEP 2: perform LDA on the user's query 
        # DO SOMETHING ... 
        # ... 
        
    
