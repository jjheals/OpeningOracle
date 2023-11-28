
from data_analysis.OpeningLDA import OpeningLDA
from scraper.Scraper import * 

from flask import jsonify 
import threading as th

class QueryHandler: 
    
    opening_lda:OpeningLDA
    index:dict[str,dict]
    
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
        print(query_tokens) 
        
        print(len(self.opening_lda.index))
        # Step 1: search the index for matches
        index_matches:dict[str,int] = [self.opening_lda.index[tok] for tok in query_tokens if tok in self.opening_lda.index]
        
        
        
        print(index_matches)
        
        # Step 2: perform LDA on the user's query 
        # DO SOMETHING ... 
        # ... 
        
    
