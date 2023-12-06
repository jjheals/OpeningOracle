import requests 
import json
from classes.Opening import *
from re import sub
from bs4 import BeautifulSoup
from os import mkdir, path
from nltk.corpus import stopwords

''' class Scraper 

    DESCRIPTION: 
        The Scraper class performs all operations for scraping data from various sources. The methods
        are separated to provide some flexibility on operations.
        
    ATTRIBUTES: 

        index (dict[str,dict[str,int]) - the index created when scrape_descriptions() is called
            - the index saves in the file at Paths.INDEX_JSON 
            - the form of the index is [key: val] == [term: {opening_code:term_freq}]
            - example:
                {
                    'center': {
                        'A00': 4,
                        'B32': 15, 
                        ...
                    },
                    ... 
                }
        
        openings_dict (OpeningsDict) - an OpeningsDict object to store the openings associated with this Scraper
            - can be created using any of the generative methods in OpeningsDict, i.e. from_json(), from_list(), etc.
        
        num_terms (dict[str,int]) - keeps track of the total number of terms for each opening (denoted by the code)
            - combines the number of terms from ALL sources of descriptions 
            - saves in Paths.NUM_TERMS_JSON
            - in the form [key: val] == [opening_code: num_terms] 
            - example: 
                { 
                    'A00': 456,
                    'B32': 942,
                    ...
                }
                
    NOTE: see each method description for in-depth details on how each method is used and the parameters
          associated with each function. 
'''
class Scraper: 
    
    # STATIC ATTRIBUTES 
    headers:dict[str,str] = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    chess_com_url:str = "https://www.chess.com/callback/eco/advanced-search?keyword=&useFavorites=false&page="
    stopwords = stopwords.words('english') 
    
    # The divs containing the content of interest for each site we scrape
    # NOTE: the keys are tuples with (attribute_type, attribute_name) where attribute_type is 0 (class) or 1 (id) 
    divs:dict[str,str] = {
        'chess.com':(0,'post-view-content'), 
        'wikipedia':(1,'mw-content-text')
    }
    
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
                   - does NOT pull opening descriptions, rather just pulls the opening names and general info from chess.com
                   - does NOT separate variations from generic openings 
    ''' 
    def get_openings(self, print_debug:bool=True, auto_save:bool=True) -> OpeningsDict:
            
        all_openings:list[Opening] = []  # List of all openings once done

        # Chess.com's opening page has 5 pages (numbered 1-5, inclusive) - collect data from each one by one and appent to all_openings as we go
        # NOTE: range(1,6) since range() is inclusive of lower bound & exclusive of upper bound
        for i in range(1,6): 
            url = Scraper.chess_com_url + str(i)                    # Format the chess.com url endpoint for this page
            response = requests.get(url, headers=Scraper.headers)   # Make the request
            openings = response.json()['items']                     # Get the 'items' object from the response; this contains the openings
            
            # Add these openings to all_openings as Opening objects
            all_openings.extend([
                                    Opening(
                                            o['name'],                                  # Name
                                            o['code'],                                  # Code 
                                            "",                                         # Color 
                                            Opening.wiki_link_from_name(o['name']),     # Wiki link
                                            o['url'],                                   # Chess.com URL
                                            o['move_list']                              # Move list (as str)
                                    ) 
                            for o in openings]
                        )
            
        # Create an openings dict obj to return and save if configured
        self.openings_dict = OpeningsDict.from_list(all_openings)
        
        # Persistent save to json
        if auto_save: self.openings_dict.dump_json()
        
        # Print info about results
        if print_debug: print(f"Scraper: done getting openings.\nSaved {len(all_openings)} results to \"{Paths.OPENINGS_JSON}.\"")
        
        # Return self.openings_dict 
        return self.openings_dict

    ''' scrape_descriptions(openings_dict) - scrape the openings' descriptions from Wikipedia and Chess.com

        PARAMETERS: 
            openings_dict (OpeningsDict) - an openings dict object containing the openings to scrape for
            
            auto_save_index (bool) - (optional) specify whether to automatically save the results in Paths.INDEX_JSON
                                   - NOTE: will override whatever currently exists in the index json
                                   
        NOTE: uses self.OpeningsDict to get the links and self.index for the index
    '''
    def scrape_descriptions(self, auto_save_index:bool=True, print_debug:bool=True) -> None: 
        
        # For tracking purposes
        num_done:int=0 
        num_openings:int=len(self.openings_dict.openings)
        mod_openings_dict:bool = False 
        
        if print_debug: print(f"Scraping {num_openings} openings...") 
        
        # Iterate over self.openings_dict.openings and visit all the URLs
        for c,v in self.openings_dict.openings.items(): 
            num_terms:int = 0   # Track the number of terms for this opening across all descriptions
            
            # Create dir to save raw content if needed 
            if not path.exists(Paths.RAW_DESC_BASE + c): mkdir(Paths.RAW_DESC_BASE + c)
            
            # Iterate over the links for this opening and get the content
            for site,url in v['links'].items(): 
                if not url: continue                                    # If there is no url, skip; some do not have chess.com or wikipedia URLs
                response = requests.get(url, headers=Scraper.headers)   # Make the request
                
                # Skip if there is an error code 
                if response.status_code != 200: 
                    if print_debug: print(f"Error getting content for \n\tCode: {c}\n\tName: {v['opening-name']}\n\tURL: {url}")
                    continue
                
                # Use BeautifulSoup to parse the HTML
                soup:BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
                
                # Save the raw content
                f = open(Paths.RAW_DESC_BASE + c + f"/{site}.txt", "w+", encoding="utf-8")
                
                '''
                # NOTE: if wikipedia, get the move list from the infobox 
                if site == "wikipedia": 
                    move_list:str = soup.find(class_="infobox-data").text
                    
                    # Save this move list in self.openings_dict
                    self.openings_dict.openings[c]['move-list'] = move_list
                    
                    # Set a flag so we know that we modified self.openings_dict
                    mod_openings_dict = True
                '''
                   
                # Get the correct div that contains the content for this link
                div_attr_type:int = Scraper.divs[site][0]   # Get the div attribute of interest (class==0 or id==1)
                div_attr_name:str = Scraper.divs[site][1]   # Get the div attribute name (ex. 'body-content')
                content:str = ''
                
                try: 
                    match(div_attr_type): 
                        case 0: content = soup.find(class_=div_attr_name).text  # Looking for class
                        case 1: content = soup.find(id=div_attr_name).text      # Looking for id
                    try: 
                        f.write(content)    # Write the content
                    except Exception as e: 
                        if print_debug: 
                            print(f"Error writing to file for description of {c} \n\tNAME: {v['opening-name']} \n\tSITE: {site}")
                            print(f"\tERROR: {e}")                         
                    f.close()           # Close the file
                    
                except AttributeError:
                    if print_debug: print(f"Error getting content for \n\tCode: {c}\n\tName: {v['opening-name']}\n\tURL: {url}")
                    f.close()
                    continue
                
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
                num_terms += len(tokens)
                
            self.num_terms[c] = num_terms   # Save the final sum of the number of terms in self.num_terms
            
            num_done+=1
            if print_debug: print(f"Done scraping for \"{c}\", \"{v['opening-name']}\" ({num_done}/{num_openings})")
        
        # If configured, save the index to Paths.INDEX_JSON and overwrite whatever exists
        if auto_save_index: 
            json.dump(self.index, open(Paths.INDEX_JSON, 'w'), indent=4)
            json.dump(self.num_terms, open(Paths.NUM_TERMS_JSON, 'w'), indent=4)
            
            self.openings_dict.dump_json()
        
        if print_debug: print(f"Scraper: Done scraping descriptions.\nNew index length = {len(self.index)}")
    
    
    ''' tokenize(text) - tokenize the given text in a standard way 
    
        PARAMETERS: 
            text (str) - the text to tokenize 
            
        RETURNS: 
            A list of strings representing the tokenized text
            
        NOTE: treats spaces, special characters, and newlines as delimeters
    ''' 
    @staticmethod
    def tokenize(text:str) -> list[str]: 
        tokens = []
        
        # Replace any special chars in the content with spaces to act as delimeters 
        pattern:str = r'[^a-zA-Z0-9\s]'     # Pattern of plaintext characters (a-z, A-Z, 0-9, no special chars)
        text = sub(pattern, ' ', text)      # Substitute all matches with spaces  
        text = sub(r'html\r\n', '', text)   # Remove the html head
        text = sub(r'\n', ' ', text)        # Remove newlines
        
        # Split the text on spaces, convert to lower, and strip whitespace from each token 
        tokens = [s.lower().strip() for s in text.split(' ') if not s.isspace() and s and not s.lower() in Scraper.stopwords]
        
        return tokens
        