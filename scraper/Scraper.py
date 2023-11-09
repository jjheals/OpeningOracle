import requests 
import json
from classes.Opening import *
from re import sub
from bs4 import BeautifulSoup

class Scraper: 
    
    # STATIC ATTRIBUTES 
    headers:dict[str,str] = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    chess_com_url:str = "https://www.chess.com/callback/eco/advanced-search?keyword=&useFavorites=false&page="
    
    # DYNAMIC ATTRIBUTES
    index:dict[str,dict[str,int]]
    openings_dict:OpeningsDict
    num_terms:dict[str,int]
    
    def __init__(self, auto_load_data:bool=False): 
        if auto_load_data: 
            self.index = json.load(open(Paths.INDEX_JSON))
            self.openings_dict = OpeningsDict.from_json()
            self.num_terms = json.load(open(Paths.NUM_TERMS_JSON))
        else: 
            self.index = {}
            self.openings_dict = OpeningsDict()
            self.num_terms = {}
    
    ''' get_openings() - get the opening names and links from chess.com and wikipedia and save the results in Paths.OPENINGS_JSON 
    
        NOTE: initially scrapes openings off chess.com (120, including variations) and creates wikipedia links off these
                   - does NOT pull all openings on wikipedia
                   - does NOT separate variations from generic openings 
    ''' 
    def get_openings(self) -> None:
            
        all_openings:list[Opening] = []  # List of all openings once done

        # Chess.com's opening page has 5 pages (numbered 1-5, inclusive) - collect data from each one by one and appent to all_openings as we go
        # NOTE: range(1,6) since range() is inclusive of lower bound & exclusive of upper bound
        for i in range(1,6): 
            url = Scraper.chess_com_url + str(i)                    # Format the chess.com url endpoint for this page
            response = requests.get(url, headers=Scraper.headers)   # Make the request
            openings = response.json()['items']                     # Get the 'items' object from the response; this contains the openings
            
            # Add these openings to all_openings as Opening objects
            all_openings.extend([Opening(o['name'], o['code'], Opening.wiki_link_from_name(o['name']), o['url'], o['move_list']) for o in openings])
            
        # Persistent save to json
        self.openings_dict = OpeningsDict.from_list(all_openings)
        self.openings_dict.dump_json()
        
        # Print info about results
        print(f"Scraper: done getting openings.\nSaved {len(all_openings)} results to \"{Paths.OPENINGS_JSON}.\"")

    ''' scrape_descriptions(openings_dict) - scrape the openings' descriptions from Wikipedia and Chess.com

        PARAMETERS: 
            openings_dict (OpeningsDict) - an openings dict object containing the openings to scrape for
            
            auto_save_index (bool) - (optional) specify whether to automatically save the results in Paths.INDEX_JSON
                                   - NOTE: will override whatever currently exists in the index json
                                   
        NOTE: uses self.OpeningsDict to get the links and self.index for the index
    '''
    def scrape_descriptions(self, auto_save_index:bool=True) -> None: 
        
        # For tracking purposes
        num_done:int=0 
        num_openings:int=len(self.openings_dict.openings)
        
        print(f"Scraping {num_openings} openings...") 
        
        # Iterate over self.openings_dict.openings and visit all the URLs
        for c,v in self.openings_dict.openings.items(): 
            for url in v['links'].values(): 
                response = requests.get(url, headers=Scraper.headers)   # Make the request
                
                # Skip if there is an error code 
                if response.status_code != 200: 
                    print(f"Error getting content for \n\tCode: {c}\n\tName: {v['opening-name']}\n\tURL: {url}")
                    continue
                
                # Use BeautifulSoup to parse the HTML
                soup:BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
                
                # Tokenize the content 
                tokens:list[str] = Scraper.tokenize(soup.text)

                # Parse the tokens and add to the index 
                for t in tokens: 
                    try:                            # If the token exists in the index already
                        tmp = self.index[t]             # Get the current dict of codes and term freqs at self.index[t]
                        if c in tmp: tmp[c] += 1        # If the current code (c) exists in the index for this token, add 1
                        else: tmp[c] = 1                # If the current code (c) does NOT exist in the index for this token, add it with term freq 1
                        self.index[t] = tmp             # Replace self.index[t] with the updated dict of codes and term freqs 
                    except KeyError:                # If the token does NOT exist in the index already
                        self.index[t] = {c:1}           # Add it with just this code (c) and 1 as the term freq
                
                # Add the number of tokens to num_terms
                self.num_terms[c] = len(tokens)
                
            num_done+=1
            print(f"Done scraping for \"{c}\", \"{v['opening-name']}\" ({num_done}/{num_openings})")
            
        # If configured, save the index to Paths.INDEX_JSON and overwrite whatever exists
        if auto_save_index: 
            json.dump(self.index, open(Paths.INDEX_JSON, 'w'), indent=4)
            json.dump(self.num_terms, open(Paths.NUM_TERMS_JSON, 'w'), indent=4)
            
        print(f"Scraper: Done scraping descriptions.\nNew index length = {len(self.index)}")
                
    @staticmethod
    def tokenize(text:str) -> list[str]: 
        tokens = []
        
        # Replace any special chars in the content with spaces to act as delimeters 
        pattern:str = r'[^a-zA-Z0-9\s]'     # Pattern of plaintext characters (a-z, A-Z, 0-9, no special chars)
        text = sub(pattern, ' ', text)      # Substitute all matches with spaces  
        text = sub(r'html\r\n', '', text) 
        
        # Split the text on spaces, convert to lower, and strip whitespace from each token 
        tokens = [s.lower().strip() for s in text.split(' ') if not s.isspace() and s]
        
        return tokens
        