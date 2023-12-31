from gensim import corpora 
from gensim.models import LdaModel
from os import listdir, path, mkdir
import json
import numpy as np

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
        
        openings (list[dict]) - list of all openings contained in Paths.OPENINGS_JSON as dictionaries
        
        num_terms (dict[str,int]) - dict containing the total number of terms in the descriptions of each opening, 
                                    used to calculate the relative tf for each 
                                    
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
    openings:dict 
    num_terms:dict 
    topic_doc_matrix:np.matrix
    
    # Parameters for LDA 
    num_topics:int                  # Number of topics for LDA
    num_passes:int                  # Number of passes through the corpus for LDA
    lda_model:LdaModel              # Trained LDA model
    dictionary:corpora.Dictionary   # Dictionary from the openings decriptions
    corpus:list[tuple]              # Corpus created by gensim.corpora
    
    def __init__(self, num_topics:int=10, num_passes:int=15, autotrain:bool=True, print_debug:bool=False):
        
        # Train LDA model if specified 
        if autotrain: 
            self.num_topics = num_topics            # Set the num topics for LDA
            self.num_passes = num_passes            # Set the num passes for LDA 
            self.texts = {}                         # Init self.texts dictionary
            self.index = json.load(open(Paths.INDEX_JSON, "r", encoding="utf-8"))
            self.openings = json.load(open(Paths.OPENINGS_JSON, "r", encoding="utf-8"))
            self.num_terms = json.load(open(Paths.NUM_TERMS_JSON, "r", encoding="utf-8"))
            
            if print_debug: print(f"Done loading data.\nlen(self.index) = {len(self.index)}\nlen(self.openings) = {len(self.openings)}\nlen(self.num_terms) = {len(self.num_terms)}")
            
            if print_debug: print("Calling OpeningLDA.__get_texts_dict__().")
            self.__get_texts_dict__()   # Load self.texts
            
            if print_debug: print("Done getting texts dict. Constructing dictionary and corpus.")
            self.dictionary = corpora.Dictionary(self.texts.values()) 
            self.corpus = [self.dictionary.doc2bow(text) for text in self.texts.values()]
            
            if print_debug: print(f"Done getting dictionary & corpus.\nlen(self.dictionary) = {len(self.dictionary)}\nlen(self.corpus) = {len(self.corpus)}")
            
            # Training 
            if print_debug: print("Training LDA model.")
            self.__lda__()
            
            if print_debug: print("Done training model. Constructing topic-doc matrix.")
            self.__construct_topic_doc_matrix__()
        else: 
            # If not autotrain, then assume this is being used to create an OpeningLDA model from a pre-trained LDA model
            # most likely using OpeningLDA.__from_pretrained_model__() via OpeningLDA.load()
            self.num_topics = -1
            self.num_passes = -1
            self.texts = {}
            self.index = {}
            self.dictionary = corpora.Dictionary()
            self.corpus = []
            self.topic_doc_matrix = None

        
    ''' __lda__() - train the LDA model from the paramters in this instance of OpeningLDA '''
    def __lda__(self):
        self.lda_model = LdaModel(self.corpus, num_topics=self.num_topics, id2word=self.dictionary, passes=self.num_passes)
    
    ''' __construct_topic_doc_matrix__() - construct a matrix of Openings and the percentage of their matched topics

        --- DESCRIPTION --- 
            Use self.lda_model & self.openings to construct self.topic_matrix in the form: 
            
                               Topic_0                Topic_1               Topic_2         . . .       Topic_K 
                               
                ECO_0 [   P(ECO_0, Topic_0)      P(ECO_0, Topic_1)      P(ECO_0, Topic_2)   . . .   P(ECO_0, Topic_K) 
                
                ECO_1     P(ECO_1, Topic_0)      P(ECO_1, Topic_1)      P(ECO_1, Topic_2)   . . .   P(ECO_1, Topic_K)
                
                ECO_2     P(ECO_2, Topic_0)      P(ECO_2, Topic_1)      P(ECO_2, Topic_2)   . . .   P(ECO_2, Topic_K)
                  .              .                       .                      .                           . 
                  .              .                       .                      .                           .
                  .              .                       .                      .                           .
                ECO_N     P(ECO_N, Topic_0)      P(ECO_N, Topic_1)      P(ECO_N, Topic_2)   . . .   P(ECO_N, Topic_K)   ]
                
        --- RETURNS --- 
            (None) Saves the resulting matrix in self.topic_matrix
    '''
    def __construct_topic_doc_matrix__(self) -> None: 
        
        # Define local variables for clarity
        P:int = len(self.texts)                    # P := number of documents (same as len(self.texts))
        N:int = self.num_topics                     # N := number of topics
        self.topic_doc_matrix:np.matrix = np.zeros((P,N))    # Create initial empty matrix (PxN)
        
        # Keep track of the ECOs in order so that we can track which matches each topic (DO NOT ALTER ORDER)
        loeco:list[str] = list(self.texts.keys())  # loeco[i] := eco code for row i in top_doc_matrix

        # Iterate through loeco and perform LDA w/ the trained model on each text from self.texts 
        for i in range(0, len(loeco)): 
            this_eco:str = loeco[i]
            
            print(f"Processing \"{this_eco}\" ({i}/{len(loeco)})")
            
            # Skip if this eco is not in self.texts, since some descriptions may have failed to be scraped
            if not this_eco in self.texts: continue
            
            # Use self.process_new_text to process the description and save the result in self.topic_doc_matrix[i]
            self.topic_doc_matrix[i] = self.process_new_text(self.texts[this_eco])
            
    ''' __get_texts_dict__() - get the saved descriptions of all the openings in self.openings
    
        --- DESCRIPTION ---
            Iterate through the subdirectories of the descriptions of each opening in self.openings, combine all 
            the descriptions (i.e. the content of each file) and save the concatenated description to
            self.texts[opening_code] (opening_code := sub_dir)
        
        --- RETURNS --- 
            (None) Populates self.texts with the appropriate combined descriptions for each opening 
    ''' 
    def __get_texts_dict__(self) -> None: 
        print("Getting texts")
        self.texts = {}
        
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
        
        print(f"New len(self.texts): {len(self.texts)}")
        
    ''' process_new_text(text) - compare a new block of text with this instance of LDA model (self.lda_model)
    
        --- DESCRIPTION --- 
            Takes as input a list of tokens as strings and uses this instance of OpeningLDA to process the given text and 
            find correlations to the already computed LDA model. 
        
        --- PARAMETERS --- 
            tokens (list[str]) - a list of tokens to process.
            pretrained_docs:list[list[str]]
            
        --- RETURNS --- 
            (list:float) The topic distribution of the input text as a vector, where the indices represent the topic id
            and the value at that index represents the % match for that topic.
    ''' 
    def process_new_text(self, tokens:str) -> list[float]:
        bow = self.dictionary.doc2bow(tokens)
        matched_topics = self.lda_model.get_document_topics(bow)
        
        # Convert the list of tuples into a list of float where the index corresponds to the topic id
        # and the value at that index corresponds to the % match for that topic
        return_vector:list[float] = [0.0 for i in range(0,self.num_topics)]
        for tup in matched_topics: return_vector[tup[0]] = tup[1]
            
        return return_vector
        
    ''' save(filename) - save this OpeningLDA model with the filename given at the path Paths.MODELS_DIR ''' 
    def save(self, filename:str) -> None:
        directory:str = Paths.MODELS_DIR + filename + "/"
        if not path.exists(directory): mkdir(directory)
        
        self.lda_model.save(directory + filename)                               # Use gensim to save the model
        corpora.MmCorpus.serialize(directory + filename + ".mm", self.corpus)   # Save the corpus
        json.dump(self.texts, open(directory + "texts.json", "w+"), indent=4)   # Save self.texts 
        json.dump(self.topic_doc_matrix.tolist(), open(directory + "matrix.json", "w+"), indent=4)   # Save self.topic_doc_matrix
        return 
        
    ''' load(filename) - load the model at the given filename in the directory Paths.MODELS_DIR 

        --- DESCRIPTION --- 
            Load a pre-trained LDA model at the path specified in Paths.MODELS_DIR/[filename] where filename is passed 
            as a parameter. 
            
        --- PARAMETERS --- 
            filename (str) - filename of the LDA model to load from Paths.MODELS_DIR
            
        --- RETURNS --- 
            An OpeningLDA object representing the trained model 
            
        --- RAISES --- 
            FileNotFoundError if the given filename does not exist in Paths.MODELS_DIR
    ''' 
    @staticmethod
    def load(filename:str) -> object: 
        if path.exists(Paths.MODELS_DIR + filename): 
            model:LdaModel = LdaModel.load(Paths.MODELS_DIR + filename + "/" + filename) 
            return OpeningLDA.__from_pretrained_model__(model, filename)
        else: 
            raise FileNotFoundError(f"Error in OpeningLDA.load(): the given filename (\"{filename}\") was not found in the directory \"{Paths.MODELS_DIR}\".")

    @staticmethod
    def __from_pretrained_model__(lda_model:LdaModel, corpus_filename:str) -> object: 
        
        # Init the object to return 
        opening_lda:OpeningLDA = OpeningLDA(autotrain=False)
        
        # Populate the parameters of the opening_lda object 
        opening_lda.lda_model = lda_model
        opening_lda.num_passes = lda_model.passes
        opening_lda.num_topics = lda_model.num_topics
        opening_lda.corpus = corpora.MmCorpus(Paths.MODELS_DIR + corpus_filename + "/" + corpus_filename + ".mm")
        opening_lda.dictionary = lda_model.id2word
        opening_lda.index = json.load(open(Paths.INDEX_JSON, "r", encoding="utf-8"))
        opening_lda.openings = json.load(open(Paths.OPENINGS_JSON, "r", encoding="utf-8"))
        opening_lda.num_terms = json.load(open(Paths.NUM_TERMS_JSON, "r", encoding="utf-8"))
        opening_lda.__get_texts_dict__()
        
        print(len(opening_lda.index))
        
        return opening_lda
        
    
    
         
        