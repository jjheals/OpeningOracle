
from flask import Flask, abort, request, jsonify     # Flask imports 
from gevent.pywsgi import WSGIServer        # To run local server
from flask_compress import Compress         # Flask compress for initialization
from flask_cors import CORS
from classes.QueryHandler import QueryHandler  # Custom import for function to handle the user's query

# --- Flask initialization --- #
app = Flask(__name__)
CORS(app)
compress = Compress()
compress.init_app(app)

query_handler = QueryHandler(load_from_file="lda")

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
        data:dict[str,str] = request.get_json()
        print(data)
        response = jsonify(query_handler.handle_user_query(data, compute_final_summary=True, debug=True))
        response.status = 200
        return response
    except Exception as e: 
        print(e)
        abort(400, description="Bad request.")

# --- RUN FOREVER --- # 
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8443), app, keyfile='privkey.pem', certfile='cert.pem')
    http_server.serve_forever()

