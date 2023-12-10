import json
from scraper.Paths import Paths 

''' class Opening

    DESCRIPTION: 

        The Opening class serves as an object to describe a single chess opening. The attributes are consistent 
        with attributes of real life chess openings, such as the name, opening moves, etc. The links are to 
        pages where information about the particular opening can be found. 
    
    ATTRIBUTES: 
    
        links (dict) - contains [key,val] as [source_name, link]
            Ex. 
                { 
                    'chess.com': 'https://chess.com/English-Opening',
                    'wikipedia': 'https://wikipedia.com/wiki/English_Opening',
                    ... 
                }
                
        opening_name (str) - the opening name (from Chess.com) 
            Ex. 'English Opening' 
            
        move_list (str) - the opening moves for this opening as a list
            Ex. ['g4', 'e5', 'h2', 'Nc6', ...]
            
        code (str) - the code for this opening
            Ex. 'A00', 'B20', 'C43', ... 
        
    NOTE: see each method description for in-depth details on how each method is used and the parameters
          associated with each function. 
'''
class Opening: 

    # STATIC ATTRIBUTES
    wiki_url_rules:dict[str] = { 
        " ": "_",                   # " " --> "_" 
        "'": "%27"                  # Apostrophe --> "%27" 
        # Add truncating after ":" manually
    }
    wiki_base_url:str = "https://en.wikipedia.org/wiki/"
    
    WHTIE:str = "white"
    BLACK:str = "black"
    DRAW:str = "draw"
    
    PRECISION:int = 3   # Precision (num dec places) for rounding success rates 
    
    # DYNAMIC ATTRIBUTES
    links:dict          # Dict of links for references to this opening
    opening_name:str    # Opening name (in the format from Chess.com) 
    move_list:str
    code:str 
    color:str
    is_variation:bool   # Is this a variation? 
    variation_name:str  # Variation name if applicable, empty string otherwise 
    success_rate:float  # Success rate of this opening when played 
    
    ''' ------------------------------- '''
    def __init__(self, opening_name:str, code:str, color:str, wiki_link:str, chess_com_link:str, move_list:str, success_rate:dict={'white':-1,'black':-1,'draw':-1}):
        self.opening_name = opening_name
        self.code = code
        self.color = color
        self.links = {
                      'wikipedia': wiki_link,
                      'chess.com': chess_com_link
                    }
        self.move_list = list(move_list)
        self.success_rate = success_rate
        
        if ':' in self.opening_name: 
            split_name:str = self.opening_name.split(':')
            self.opening_name = split_name[0].strip()
            self.is_variation = True
            self.variation_name = split_name[1].strip()
        elif ',' in self.opening_name: 
            split_name:str = self.opening_name.split(',')
            self.opening_name = split_name[0].strip()
            self.is_variation = True
            self.variation_name = ','.join(split_name[1:]).strip()
        else: 
            self.is_variation = False
            self.variation_name = ""
            
    ''' ------------------------------- '''
    ''' to_dict() - convert this opening to a dictionary format '''
    def to_dict(self) -> dict: 
        return {
                'code': self.code, 
                'color': self.color,
                'opening-name': self.opening_name, 
                'move-list': self.move_list, 
                'links': self.links,
                'is-variation': self.is_variation,
                'variation-name': self.variation_name,
                'success-rate': self.success_rate
            }
    
    ''' ------------------------------- '''
    ''' to_string() - convert this opening to a meaningful, readable string (to print, etc.) '''
    def to_string(self) -> str: 
        s = f"Name: {self.opening_name}\n"          # Name
        s += f"Color: {self.color}\n"               # Color
        s += f"Variation?: {self.is_variation}\n"   # Is variation? 
        
        # Include variation name if it is a variation
        if self.is_variation: s += f"Variation: {self.variation_name}\n"
        
        s += f"Code: {self.code}\n"                   # Code
        s += f"Moves: {self.move_list}\n"             # Moves
        s += f"Success Rate: {self.success_rate}\n"   # Success rate
        
        # Links
        s += "Links: \n"                             
        for k,l in self.links.items(): s += f"\t{k} - {l}\n"    
         
        return s
    
    ''' ------------------------------- '''
    ''' opening_from_dict(d) - create an Opening object from a given dictionary
    
        PARAMETERS: 
            d (dict) - dictionary matching the format of an opening, i.e., in the format from PATHS.OPENINGS_JSON
        
        RETURNS: 
            An Opening object       
    '''
    @staticmethod
    def opening_from_dict(d:dict) -> object: 
        o = Opening(d["opening-name"], d['code'], d["color"], d["links"]["wikipedia"], d["links"]["chess.com"], d['move-list'], d['success-rate'])
        return o
    
    ''' ------------------------------- '''
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
        
        # Truncate on ":" and "," to get rid of variations
        if ":" in name: name = name.split(":")[0]
        if "," in name: name = name.split(",")[0]
        
        return Opening.wiki_base_url + name
    
    
''' class OpeningsDict
   
   DESCRIPTION: 
   
        The OpeningsDict class serves as an easy way to store groups of Opening objects. The methods 
        contained in this class intend to standardize saving groups of openings to persistent storage,
        i.e. openings.json, and aim to provide single methods for performing operations on openings. 
        The main objective of OpeningsDict is to provide organization and simplicity around the structure
        and implementation of persistent storage and operations on groups of Openings.
   
   ATTRIBUTES: 
        openings (dict) - contains [key,val] as [opening_id, opening_as_dict]        
        
    NOTE: see each method description for in-depth details on how each method is used and the parameters
          associated with each function. 
'''
class OpeningsDict: 
    
    # DYNAMIC ATTRIBUTES
    openings:dict[str, dict]
    
    def __init__(self): 
        self.openings = {}
        
    ''' to_json() - convert this OpeningLinks to a json file '''
    def dump_json(self) -> None: json.dump(self.openings, open(Paths.OPENINGS_JSON, "w"), indent=4)
        
    ''' from_json() - create an OpeningLinks object from a json file '''
    @staticmethod 
    def from_json() -> object: 
        opening_links = OpeningsDict()
        opening_links.openings = json.load(open(Paths.OPENINGS_JSON, "r"))
        return opening_links
    
    ''' from_list(loo) - create an OpeningsDict object from a given list of Opening

        NOTE: the names in this object (the keys) are based on the chess.com variation and should be
              standardized to match the specific links when needed
              
        PARAMETERS: 
            loo (list[Opening]) - list of Opening objects 
            
        RETURNS: 
            An OpeningDicts object
    '''
    @staticmethod
    def from_list(loo:list[Opening]) -> object: 
        d = {}
        for o in loo: d[o.code] = o.to_dict()
        
        o_dict = OpeningsDict()
        o_dict.openings = d
        
        return o_dict
    

    ''' concet(lod) - create a single OpeningsDict object from a given list of OpeningsDicts '''
    @staticmethod
    def concat(lod:list) -> object:
        combined_dict = lod[0]
        
        # Find out which OpeningsDict is largest from the given ones and use this as the base 
        for d in lod: 
            if len(d.openings) > len(combined_dict.openings): combined_dict = d
        
        # Now, iterate through each given openings dict again and compare the contents to combined_dict, 
        # while updating combined_dict if needed
        for d in lod: 
            for eco,new_opening in d.openings.items(): 
                
                # Case 0 (base case): the eco code does NOT already exist in combined dict
                if not eco in combined_dict.openings: combined_dict.openings[eco] = new_opening
                
                # Case 1: the eco code DOES exist in combined dict 
                else: 
                    stored_opening:dict = combined_dict.openings[eco]
                    
                    # Check each attribute of the opening in combined_dict to see if it needs to be set or updated
                    # Update the success rates (negligible time)
                    stored_successes = stored_opening['success-rate']
                    average_successes = { key: abs(round((new_opening['success-rate'][key] + stored_successes[key]) / 2, Opening.PRECISION)) for key in stored_successes }                    
                    stored_opening['success-rate'] = average_successes
                    
                    # Update the side/color
                    if not stored_opening['color']: stored_opening['color'] = new_opening['color']
                    
                    # Update the move list 
                    if not stored_opening['move-list']: stored_opening['move-list'] = new_opening['move-list']
                    
                    # Update the links
                    for site,url in new_opening['links'].items(): 
                        if not site in stored_opening['links']: stored_opening['links'][site] = url
                                        
                    # Resave the updated stored_opening in combined_dict
                    combined_dict.openings[eco] = stored_opening
                    
        return combined_dict