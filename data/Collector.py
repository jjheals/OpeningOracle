import pandas as pd

from scraper.Scraper import Scraper
from scraper.Paths import Paths
from classes.Opening import *

class Collector: 
    
    def __init__(self, ): 
        pass
    
    ''' collect_all_data() - collect all the data from the various sources
    
        --- DESCRIPTION --- 
            Collects all the data needed from all sources. Steps: 
                1. Use the Scraper class (scraper/Scraper.py) to get the openings from chess.com
                
                2. Use the Kaggle dataset (data/kaggle-lichess.csv) to get more opening names/codes
                   AND to calculate the success rates for each opening
                   
                3. Merge the results of step 1 and step 2 to create a single OpeningsDict object containing
                   all the openings from both sources
                   
                4. Scrape the descriptions for all openings 
                
                5. Save the results in the relevant JSON files and descriptions in the relevant directories   
                    
                    Files modified: 
                        => index -> data/index.json
                        => openings -> data/openings.json
                        => num terms in descs -> data/num_terms.json 
                        => raw descriptions -> data/raw_descs/[code]/[chess.com.txt | wikipedia.txt]

        --- PARAMETERS --- 
            print_debug (bool) - specify whether to print the debug information while running. Default == True
        
        --- RETURNS --- 
            (None) Returns nothing but saves all results in the relative locations.
    '''
    def collect_all_data(self, print_debug:bool=True) -> None: 
        if print_debug: print("NOTICE: Collector - Starting data collection.")
        
        # Init classes and load dataset
        scraper = Scraper()                                 # Init scraper 
        
        # Load the datasets 
        lichess_df = pd.read_csv(Paths.LICHESS_DATASET)                     
        openings_df:pd.DataFrame = pd.read_csv(Paths.OPENINGS_DATASET)
        

        # STEP 1: use scraper to get the openings from chess.com 
        chess_com_openings:OpeningsDict = scraper.get_openings(auto_save=False) 
       
        # STEP 2: Processing the datasets
        lichess_ds_dict:OpeningsDict = Collector.__process_lichess_dataset__(lichess_df)
        openings_ds_dict:OpeningsDict = Collector.__process_openings_dataset__(openings_df)   

        # STEP 3: combine the results from the scraper and the two datasets into one openings dict obj
        
        # Load the openings.json, and add the openings that we just created IF AND ONLY IF they do not exist already
        # NOTE: it is important that they do not already exist (that the code does not exist) so we don't overwrite 
        #       data we have
        combined_openings_dict:OpeningsDict = OpeningsDict.concat([chess_com_openings, lichess_ds_dict, openings_ds_dict])

        if print_debug: 
            print("NOTICE: Collector - Done getting openings from Scraper, Lichess dataset, & Openings dataset.")
            print(f"NOTICE: Collector - Saving Openings to \"{Paths.OPENINGS_JSON}\". Starting to scrape descriptions.")
        
        # Dump openings_dict to Paths.OPENINGS_JSON
        combined_openings_dict.dump_json()
        
        # Scrape the descriptions
        scraper = Scraper(auto_load_data=True)                # Reinit scraper to reload the openings json
        scraper.scrape_descriptions(print_debug=print_debug)  # Call scraper.scrape_descriptions
        
        if print_debug: print("Collector.collect_all_data() - DONE.")
        
        
    ''' __process_openings_dataset__(df) - process the openings dataset (Paths.OPENINGS_DATASET) ''' 
    @staticmethod 
    def __process_openings_dataset__(df:pd.DataFrame) -> OpeningsDict: 
        print("Processing openings dataset")
        df.fillna("", inplace=True)                 # Replace NaN with empty string 
        return_dict:OpeningsDict = OpeningsDict()   # Create an OpeningsDict obj to return in the correct format

        # Cut the df down to the columns we care about
        columns = ['opening_name', 'side', 'ECO', 'perc_white_win', 'perc_draw', 'perc_black_win', 'move1w', 'move1b', 'move2w', 'move2b', 'move3w', 'move3b', 'move4w', 'move4b']
        df = df[columns]        
            
        # Now iterate through ALL the ecos of the df and combine the average results into the return dict values for that eco
        for eco in df['ECO'].unique():     
                   
            # Get all the matches in the df for this eco
            row_matches = df.loc[df['ECO'] == eco]                       
            white_avg:float = round(sum(row_matches['perc_white_win']) / 100 / len(row_matches), Opening.PRECISION)
            black_avg:float = round(sum(row_matches['perc_black_win']) / 100 / len(row_matches), Opening.PRECISION)
            draw_avg:float = round(sum(row_matches['perc_draw']) / 100 / len(row_matches), Opening.PRECISION)
        
            these_success_rates:dict[str,float] = { 
                             'white': white_avg,
                             'black': black_avg,
                             'draw': draw_avg     
                        }
                        
            first_match = list(row_matches.iterrows())[0][1]            
            opening_name:str = str(first_match['opening_name'])
            side:str = first_match['side']
            move_list:list[str] = [
                                    first_match['move1w'],    # move1w
                                    first_match['move1b'],    # move1b
                                    first_match['move2w'],    # move2w    
                                    first_match['move2b'],    # move2b
                                    first_match['move3w'],    # move3w
                                    first_match['move3b'],    # move3b
                                    first_match['move4w'],    # move4w
                                    first_match['move4b']     # move 4b
                                ]
            
            
            new_opening:Opening = Opening(opening_name, eco, side, Opening.wiki_link_from_name(opening_name), "", move_list,these_success_rates)
            return_dict.openings[eco] = new_opening.to_dict()

        return return_dict
    
    ''' __process_lichess_dataset__(df) - process the lichess dataset (Paths.LICHESS_DATASET) ''' 
    @staticmethod
    def __process_lichess_dataset__(df:pd.DataFrame) -> OpeningsDict:
        return_dict:OpeningsDict = OpeningsDict()
        
        for eco in df['opening_eco'].unique():

            matches:pd.DataFrame = df.loc[df['opening_eco'] == eco]
            opening_name:str = list(matches['opening_name'])[0]
            
            white_wins:pd.DataFrame = matches.loc[matches['winner'] == 'white']
            black_wins:pd.DataFrame = matches.loc[matches['winner'] == 'black']
            draws:pd.DataFrame = matches.loc[matches['winner'] == 'draw']
            
            success_rates = { 
                                'white': round(len(white_wins) / len(matches), Opening.PRECISION),
                                'black': round(len(black_wins) / len(matches), Opening.PRECISION),
                                'draw': round(len(draws) / len(matches), Opening.PRECISION)
            }

            lich_new_opening:Opening = Opening(opening_name, eco, "", Opening.wiki_link_from_name(opening_name), "", success_rates)
            return_dict.openings[eco] = lich_new_opening.to_dict()
        
        return return_dict