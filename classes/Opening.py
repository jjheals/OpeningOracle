import json
from scraper.Paths import Paths 

''' Opening - class for Openings as objects 

    ATTRIBUTES: 
        links (dict) - contains [key,val] as [source_name, link]
        opening_name (str) - the opening name (from Chess.com) 

'''
class Opening: 
    
    # STATIC ATTRIBUTES
    wiki_url_rules:dict[str] = { 
        " ": "_",                   # " " --> "_" 
        "'": "%27"                  # Apostrophe --> "%27" 
        # Add truncating after ":" manually
    }
    wiki_base_url:str = "https://en.wikipedia.org/wiki/"
    
    # DYNAMIC ATTRIBUTES
    links:dict          # Dict of links for references to this opening
    opening_name:str    # Opening name (in the format from Chess.com) 
    move_list:str
    code:str 
    
    def __init__(self, opening_name:str, code:str, wiki_link:str, chess_com_link:str, move_list:str):
        self.opening_name = opening_name
        self.code = code
        self.links = {
                      'wikipedia': wiki_link,
                      'chess.com': chess_com_link
                    }
        self.move_list = move_list
    
    ''' to_dict() - convert this opening to a dictionary format '''
    def to_dict(self) -> dict[str,str]: 
        return {'code': self.code, 'opening-name': self.opening_name, 'move-list': self.move_list, 'links': self.links}
    
    ''' to_string() - convert this opening to a meaningful, readable string (to print, etc.) '''
    def to_string(self) -> str: 
        print(f"Called to string on {self.opening_name}")
        s = f"Name: {self.opening_name}\n"                      # Name
        s += f"Code: {self.code}"                               # Code
        s += f"Moves: {self.move_list}"                         # Moves
        s += "Links: \n"                                        # Links
        for k,l in self.links.items(): s += f"\t{k} - {l}\n"    
         
        return s
    
    ''' opening_from_dict(d) - create an Opening object from a given dictionary
    
        PARAMETERS: 
            d (dict) - dictionary matching the format of an opening, i.e., in the format from PATHS.OPENINGS_JSON
        
        RETURNS: 
            An Opening object       
    '''
    @staticmethod
    def opening_from_dict(d:dict) -> object: 
        o = Opening(d["opening-name"], d['code'], d["links"]["wikipedia"], d["links"]["chess.com"], d['move_list'])
        
        return o
    
    ''' wiki_link_from_name(name) - create a wikipedia link from the given name 
    
        PARAMETERS: 
            name (str) - opening name from Chess.com
            
        RETURNS: 
            The wikipedia link for this name as a string     
    '''
    @staticmethod
    def wiki_link_from_name(name:str) -> str: 
        for k,v in Opening.wiki_url_rules.items(): 
            name = name.replace(k,v)
        
        # Truncate on ":" to get rid of variations
        if ":" in name: name = name.split(":")[0]
        
        return Opening.wiki_base_url + name
    
    
''' OpeningsDict - class to create an object to store the openings with an ID 
   
   ATTRIBUTES: 
        openings (dict) - contains [key,val] as [opening_id, opening_as_dict]                 
'''
class OpeningsDict: 
    
    # DYNAMIC ATTRIBUTES
    openings:dict[str, dict]
    
    def __init__(self): 
        self.openings = {}
        
    ''' to_json() - convert this OpeningLinks to a json file '''
    def to_json(self) -> None: json.dumps(self.openings, open(Paths.OPENINGS_JSON, "w"))
        
    ''' from_json() - create an OpeningLinks object from a json file '''
    @staticmethod 
    def from_json() -> object: 
        opening_links = OpeningsDict()
        opening_links.openings = json.load(open(Paths.OPENINGS_JSON, "r"))
        return opening_links
    
    ''' from_list(loo) - create an OpeningLinks object from a given list of Opening

        NOTE: the names in this object (the keys) are based on the chess.com variation and should be
              standardized to match the specific links when needed
              
        PARAMETERS: 
            loo (list[Opening]) - list of Opening objects 
            
        RETURNS: 
            An OpeningLinks object
    '''
    @staticmethod
    def from_list(loo:list[Opening]) -> object: 
        d = {}
        for o in loo: d[o.opening_name] = o.links
        
        opening_links = OpeningsDict()
        opening_links.openings = d
        
        return opening_links
    

