import requests 
import json
from classes.Opening import *

class Scraper: 
    
    # STATIC ATTRIBUTES 
    headers:dict[str,str] = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    chess_com_url:str = "https://www.chess.com/callback/eco/advanced-search?keyword=&useFavorites=false&page="
    
    def __init__(self): 
        pass
    
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
            all_openings.extend([Opening(o['name'], Opening.wiki_link_from_name(o['name']), o['url'], o['move_list']) for o in openings])
            
        # Persistent save to json
        json.dump([o.to_dict() for o in all_openings], open(Paths.OPENINGS_JSON, 'w'), indent=4)
        
        # Print info about results
        print(f"Scraper: done getting openings.\nSaved {len(all_openings)} results to \"{Paths.OPENINGS_JSON}.\"")

    ''' scrape_descriptions() - scrape the openings' descriptions from Wikipedia and Chess.com

        NOTE: uses the openings and links contained in Paths.OPENINGS_JSON
    '''
    def scrape_descriptions(self) -> None: 
        pass
        