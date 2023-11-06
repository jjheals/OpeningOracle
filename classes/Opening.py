class Opening: 
    
    links:dict
    wiki_link:str
    opening_name:str
    
    def __init__(self, opening_name:str, wiki_link:str, chess_com_link:str):
        self.opening_name = opening_name
        self.links = {
                      'wikipedia': wiki_link,
                      'chess.com': chess_com_link
                    }
        
    def to_dict(self) -> dict[str,str]: 
        return {'opening-name': self.opening_name, 'links': self.links}
    
    
    def to_string(self) -> str: 
        s = f"Name: {self.opening_name}\n"
        s += "Links: \n"

        for s,l in self.links.items(): s += f"\t{s} - {l}\n"
        
        return s
    
    