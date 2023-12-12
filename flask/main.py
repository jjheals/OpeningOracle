
from flask import Flask, abort, request     # Flask imports 
from gevent.pywsgi import WSGIServer        # To run local server
from flask_compress import Compress         # Flask compress for initialization

from QueryHandler import handle_user_query  # Custom import for function to handle the user's query

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
                "user=query": "a single string of the user's query (literal)",
            }
    
    --- RETURN FORMAT ---  
        [+] Data: application/json
            {
                ' ': ' ', 
                ...
            }

'''
@app.route('/postRequestOpening', methods=['POST'])
def lookup():
    try: 
        data:dict[str,str] = request.get_json()
        return handle_user_query(data)
    except: 
        abort(400, description="Bad request.")


# --- RUN FOREVER --- # 
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()