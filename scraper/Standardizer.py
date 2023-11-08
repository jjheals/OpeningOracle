import pandas as pd
from Paths import Paths

class Standardizer:

    def __init__(self): 
        pass

    def standardize_elos(self):
        kaggle = pd.read_csv(Paths.LICHESS_DATASET)
        #print(kaggle)
        for entry in kaggle:
            print(entry)
            
standardizer = Standardizer()
standardizer.standardize_elos()