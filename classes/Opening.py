class Opening: 
    
    wiki_link:str
    opening_name:str
    
    def __init__(self, opening_name:str, wiki_link:str):
        self.wiki_link = wiki_link
        self.opening_name = opening_name
    
    def to_dict(self) -> dict[str,str]: 
        return {'opening-name': self.opening_name, 'wiki-link': self.wiki_link}
    
    
    def to_string(self) -> str: 
        return f"Name: {self.opening_name}\nWikipedia: {self.wiki_link}"
    
    