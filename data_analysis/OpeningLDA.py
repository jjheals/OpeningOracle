from gensim import corpora 
from gensim.models import LdaModel
from os import listdir
import json

from scraper.Paths import Paths     # For static paths to files & directories
from scraper.Scraper import Scraper # For tokenize()

''' class OpeningLDA 

    DESCRIPTION: 
        The OpeningLDA class serves as a wrapper for an LDA model based on the structure of the data collected
        for the chess openings. The actual trained LDA model is instantiated on initialization of the class and
        can be accessed via the lda_model attribute. The LDA model is trained using the raw descriptions of the 
        openings (stored in Paths.RAW_DESC_BASE) by combining the descriptions from each source for each
        individual opening, tokenizing the combined description, and using these tokens with respect to each 
        opening to train the LDA model. 
        
    ATTRIBUTES: 

        docs_path (str) - static attribute for the path to the raw descriptions of the Openings
        
        texts (dict[str,listr[str]]) - a dictionary with (key:val) -> (opening_code:tokenized_descriptions) where
                                       tokenized_descriptions is a single list containing the tokenized versions 
                                       of the descriptions for each opening

        index (dict[str,dict[str,int]]) - a dictionary with (key:val) -> (term:{opening_code:term_freq}); i.e. the 
                                          index created by the scraper and stored at Paths.INDEX_JSON
        
        num_topics (int) - optional: the number of topics to use for training the LDA model. Default = 10
        
        num_passes (int) - optional: the number of passes through the corpus for the LDA model. Default = 15
        
        lda_model (LdaModel) - the trained LDA model, instantiated upon initialization of an instance of the class
                               (called within __init__())
        
        dictionary (corpora.Dictionary) - a dictionary mapping words to numerical IDs. NOTE: is not a dict as in Python dict
                                          but rather is a corpus dictionary used by LDA
        
        corpus (list[tuple]) - a list of tuples returned by doc2bow()   

    NOTE: see each method description for in-depth details on how each method is used and the parameters
          associated with each function. 
'''
class OpeningLDA: 
    
    # STATIC ATTRIBUTES
    docs_path:str = Paths.RAW_DESC_BASE
    
    # DYNAMIC ATTRIBUTES
    texts:dict[str,list[str]] 
    index:dict[str,dict[str,int]]
    
    # Parameters for LDA 
    num_topics:int                  # Number of topics for LDA
    num_passes:int                  # Number of passes through the corpus for LDA
    lda_model:LdaModel              # Trained LDA model
    dictionary:corpora.Dictionary   # Dictionary from the openings decriptions
    corpus:list[tuple]              # Corpus created by gensim.corpora
    
    def __init__(self, num_topics:int=10, num_passes:int=15):
        self.num_topics = num_topics            # Set the num topics for LDA
        self.num_passes = num_passes            # Set the num passes for LDA 
        self.texts = {}                         # Init self.texts dictionary
        self.index = json.load(open(Paths.INDEX_JSON, "r", encoding="utf-8"))
        
        # Iterate through the subdirectories of the descriptions of each opening and save the combined description 
        # of all files for that opening to self.texts[opening_code] (opening_code := sub_dir)
        for sub_dir in listdir(OpeningLDA.docs_path): 
            comb_descs:list[str] = [] # Init var for the combined descriptions
            
            # Iterate through the files in this sub directory and add the content to comb_descs
            all_filenames:list[str] = listdir(OpeningLDA.docs_path + sub_dir)
            for filename in all_filenames: 
                with open(OpeningLDA.docs_path + sub_dir + "/" + filename, "r", encoding="utf-8") as file: 
                    comb_descs.extend(Scraper.tokenize(file.read()))
            
            # Save the combined description in self.texts
            self.texts[sub_dir] = comb_descs
            
        self.dictionary = corpora.Dictionary(self.texts.values()) 
        self.corpus = [self.dictionary.doc2bow(text) for text in self.texts.values()]

        # Train LDA model
        self.__lda__()
    
    
    ''' __lda__() - train the LDA model from the paramters in this instance of OpeningLDA '''
    def __lda__(self):
        self.lda_model = LdaModel(self.corpus, num_topics=self.num_topics, id2word=self.dictionary, passes=self.num_passes)