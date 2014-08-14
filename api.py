#-------------------------------------------------------------------------------
# Name:        api
# Purpose:     api for asset tracking
#
# Author:      a

# Licence:     MIT
#-------------------------------------------------------------------------------
from flask import Flask, render_template, request, redirect, session, abort
from flask.ext.basicauth import BasicAuth
import os
from pymongo import MongoClient
from OpenSSL import SSL
import random
import string

#MongoDB settings
def connect():
    connection = MongoClient("localhost",27017)
    handle = connection["apitest1"]
    handle.authenticate("user","pw")
    return handle

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
handle = connect()

#SOME SECURITY

#for CSRF attacks
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = \
        ''.join(random.choice(string.ascii_uppercase + string.digits) \
        for _ in range(10))
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

#for SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('ast.key')
context.use_certificate_file('ast.crt')

#some basic authentication
app.config['BASIC_AUTH_USERNAME'] = 'user'
app.config['BASIC_AUTH_PASSWORD'] = 'pw'
basic_auth = BasicAuth(app)

def reporter_auth(key):
    """This function is called to verify reporter hardware"""
    return key == 'yoimareporter'
def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You are not authenticated', 401,
    {'WWW-Authenticate': 'Basic realm="Auth Required"'})
def req_reporter_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not reporter_auth(auth.key):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#MAIN ROUTES
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/upsert", methods=['GET'])
@basic_auth.required
def upsert():
    userinputs = [x for x in handle.trackingdb.find()]
    return render_template('upsert.html', userinputs=userinputs)

@app.route("/find", methods=['GET'])
def find():
    return render_template('find.html')

@app.route("/report", methods=['GET'])
@basic_auth.required
def report():
    userinputs = [x for x in handle.trackingdb.find()]
    return render_template('report.html', userinputs=userinputs)

@app.route("/findassetread", methods=['POST'])
def findassetread():
    form1 = {
            "assetid": request.form.get("asset")
            }
    queries = handle.trackingdb.find(form1)
    return render_template('find.html', queries=queries)

@app.route("/findtagread", methods=['POST'])
def findtagread():
    form1 = {
            "tagid": request.form.get("tag")
            }
    queries = handle.trackingdb.find(form1)
    return render_template('find.html', queries=queries)

@app.route("/findreaderread", methods=['POST'])
def findreaderread():
    form1 = {
            "readerid": request.form.get("reader")
            }
    queries = handle.trackingdb.find(form1)
    return render_template('find.html', queries=queries)

#WRITE FUNCTIONS
@app.route("/upsertwrite", methods=['POST'])
@basic_auth.required
def upsertwrite():
    tag1 = {"tagid": request.form.get("tag"), \
            "readerid": request.form.get("reader"),\
            "readerid2": request.form.get("reader"),\
            "readerid3": request.form.get("reader"),\
            "readerid4": request.form.get("reader"),\
            "readerid5": request.form.get("reader")}
    query = {"assetid": request.form.get("asset")}
    assetid = handle.trackingdb.update(query,{"$set": tag1},**{'upsert':True})
    return redirect ("/upsert")

@app.route("/reportwrite", methods=['POST'])
@basic_auth.required
def reportwrite():
    location = request.form.get('reader')
    query = {"tagid": request.form.get('tag')}
    retrieve = handle.trackingdb.find_one(query)

    def replace_value(key_to_find, value):
        for key in retrieve.keys():
            if key == key_to_find:
                retrieve[key] = value

    if location != retrieve.get("readerid", ""):
        replace_value("readerid5", retrieve.get("readerid4", ""))
        replace_value("readerid4", retrieve.get("readerid3", ""))
        replace_value("readerid3", retrieve.get("readerid2", ""))
        replace_value("readerid2", retrieve.get("readerid", ""))
        replace_value("readerid", location)

        assetid = handle.trackingdb.update({},retrieve)

    return redirect ("/report")

@app.route("/deleteall", methods=['GET'])
@basic_auth.required
def deleteall():
    handle.trackingdb.remove()
    return redirect ("/")

# Remove the "debug=True" for production
if __name__ == '__main__':
    app.run(host='localhost',debug=True,port=5000,ssl_context=context)