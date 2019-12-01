from flask import Flask, Response, make_response, request
from flask_sslify import SSLify
from flask_cors import CORS
import os
import requests
from client_jwt import create_client_jwt
import json

WEBDIR = os.path.abspath("../")

app = Flask(__name__)
sslify = SSLify(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')    
def route_all(path):
    if ".." in path or path.startswith("/") or "//" in path:
        return "FU"
        
    if not path:
        path = "index.html"
 
    fpath = os.path.join(WEBDIR, path)
    if os.path.isdir(fpath):
        return "Dir!"
    elif os.path.isfile(fpath):
        resp = make_response(open(fpath, "rb").read())
        _, ext = os.path.splitext(fpath)
        if ext == ".js":
            resp.headers["Content-Type"] = "text/javascript"
        elif ext == ".css":
            resp.headers["Content-Type"] = "text/css"
        return resp
    elif os.path.exists(fpath):
        return "Unk file type"
    return "404"

@app.route("/avoid-cors/<path:url>", methods=[ "POST"])
def avoid_cors(url):    
   
    auth_msg = request.get_json()
    print(auth_msg)
    import pdb; pdb.set_trace() 
    #resp = requests.post(URL, json=auth_msg, headers={"Authorization": "Bearer %s" % (encoded_jwt)})
    resp = requests.post("https://%s" % (url), data=request.data, headers=dict(request.headers) )
    print(resp.content)
    res = make_response(resp.content)
    res.headers = dict(resp.headers)
    res.headers["Access-Control-Allow-Origin"] = "*"
   
    return res, resp.status_code
 

if __name__ == "__main__":
    # app.run(debug=True, port=4580)
     context = ('server3.crt', 'server3.key')
     app.run(debug=True, ssl_context=context, port=4580)
    #app.run( debug = True, ssl_context = 'adhoc')  # Generate Adhoc Certs