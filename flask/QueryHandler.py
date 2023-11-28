from OpeningOracle.classes import * 
from OpeningOracle.data_analysis import *

from flask import jsonify 
import threading as th


''' handle_user_query(query) - handles a query by a user 

    --- DESCRIPTION --- 
        Takes as input the query by a user, i.e. the user's description of their playstyle, and 
        returns a dictionary (JSON object) in the correct format for the client-side to render 
        on the page. 
        
        First takes the query and tokenizes it to search the index, stores the matches in descending
        order of relevance. 
        
        Second takes the query and compares it to pre-computed LDA results from all possible openings, 
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
'''
def handle_user_query(query:dict[str,str]) -> dict[str,list[str]]: 
    
    # NOTE: perform step 2 BEFORE step 1, since we can run step 2 as a separate thread 
    #       to slightly improve the runtime 
    nlp_thread:th.Thread = th.Thread()
    nlp_thread.start()
    
    
    
    # Step 2: perform LDA on the user's query 
    
    # Step 1: tokenize the query and search the index for matches
    index_matches = []
    
    # DO SOMETHING ... 
    # ... 
