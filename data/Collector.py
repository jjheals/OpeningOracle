import pandas as pd

from scraper.Scraper import Scraper
from scraper.Paths import Paths
from classes.Opening import *

class Collector: 
    
    def __init__(self, ): 
        pass
    
    def collect_all_data(self, print_debug:bool=True) -> None: 
        if print_debug: print("NOTICE: Collector - Starting data collection.")
        
        # Init classes and load dataset
        scraper = Scraper()                         # Init scraper 
        df = pd.read_csv(Paths.LICHESS_DATASET)     # Load kaggle dataset
        scraper.get_openings()                      # Gets the openings from chess.com and saves in openings.json
        openings_dict:OpeningsDict = OpeningsDict.from_json()   # Load the openings we just got as an OpeningsDict object so we can modify them

        if print_debug: 
            print("NOTICE: Collector - Done getting openings from Scraper.")
            print("NOTICE: Collector - Starting dataset aggregation & analysis.")
        
        # Add the Kaggle dataset Openings to our dict of openings
        all_names:list[str] = list(df['opening_name'])
        all_codes:list[str] = list(df['opening_eco'])
        all_openings:list[Opening] = []
        
        # Convert all the names to Openings 
        for n,c in zip(all_names, all_codes): 
            new_opening:Opening = Opening(n, c, Opening.wiki_link_from_name(n), "", "")
            all_openings.append(new_opening)

        # Create an OpeningsDict object to get the correct format for openings.json
        openings_dict2:OpeningsDict = OpeningsDict.from_list(all_openings)

        # Load the openings.json, and add the openings that we just created IF AND ONLY IF they do not exist already
        # NOTE: it is important that they do not already exist (that the code does not exist) so we don't overwrite 
        #       data we have
        print(f"Original len(openings_dict): {len(openings_dict.openings)}")

        for c,d in openings_dict2.openings.items(): 
            if c in openings_dict.openings: continue  # SKIP if code exists already
            openings_dict.openings[c] = d             # ADD if code does not exist 

        print(f"New len(openings_dict): {len(openings_dict.openings)}")
        
        # Calculate the success rates from the Kaggle dataset 
        # Create a dict of the succcess rates for all openings in the dataset
        opening_success_rates:dict = {                                                                                                                                           
                                    c: { 
                                        'white':0.0, 
                                        'black':0.0, 
                                        'draw':0.0 
                                    } 
                                for c in df['opening_eco']
                                }
        
        # Parse the dataset and calculate the win percentages for white & black for each opening 
        for code in opening_success_rates.keys():
            sub_df:pd.DataFrame = df.loc[df['opening_eco'] == code]
            white_wins:pd.DataFrame = sub_df.loc[sub_df['winner'] == 'white']
            black_wins:pd.DataFrame = sub_df.loc[sub_df['winner'] == 'black']
            draws:pd.DataFrame = sub_df.loc[sub_df['winner'] == 'draw']
            
            opening_success_rates[code] = { 
                                'white': round(len(white_wins) / len(sub_df), 3),
                                'black': round(len(black_wins) / len(sub_df), 3),
                                'draw': round(len(draws) / len(sub_df), 3)
            }
            
        # Now add these new success-rates to the actual dictionary of all openings 
        for c,d in opening_success_rates.items():
            try: openings_dict.openings[c]['success-rate'] = d
            except KeyError: print(c)
            
        # Dump openings_dict
        openings_dict.dump_json()
        
        # Scrape the descriptions
        scraper = Scraper(auto_load_data=True) 
        scraper.scrape_descriptions()