
from flask import Flask, abort, request     # Flask imports 
from gevent.pywsgi import WSGIServer        # To run local server
from flask_compress import Compress         # Flask compress for initialization

from classes.QueryHandler import handle_user_query  # Custom import for function to handle the user's query

# --- Flask initialization --- #
app = Flask(__name__)
compress = Compress()
compress.init_app(app)


# --- Endpoints --- #
 
''' @app.route('/postRequestOpening') - endpoint to submit a user query

    --- DESCRIPTION ---  
        Handles the user's query as a JSON object via a POST request and returns a JSON object containing
        the data to display to the user. 
        
    --- REQUEST FORMAT ---   
        [+] Methods - 
                POST

        [+] Data: application/json
            {
                "message": "a single string of the user's query (literal)",
                "color": "white" | "black" (literal) 
            }
    
    --- RETURN FORMAT ---  
        [+] Data: application/json
            - JSON object with a single key "messages" with the value as a list of matched openings 
              ranked in descending order by relevance/relation to user's description. 
              
            {
                "messages": [
                    "Description of match 1 ...",
                    "Description of match 2 ...",
                    "..." 
                ]
            }
'''
@app.route('/postRequestOpening', methods=['POST'])
def lookup():
    try: 
        return_dict = { 
                    "messages": [ 
                        "You should try the Queens Gambit! It starts with 1. e4 f5 2. e4xf5 ...", 
                        "I think you should try the King's Gambit! It's a relatively aggressive opening that attempts to capture the center with 1. ... g5 2. ... Nf6 ...",
                        "The King's Indian would work well for you! It allows you to king-side castle quickly, and opens the dark-squared bishop across the board."   
                    ]   
                       
        }
        return return_dict
    except: 
        abort(400, description="Bad request.")


# --- RUN FOREVER --- # 
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
