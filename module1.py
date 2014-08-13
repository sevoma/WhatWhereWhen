#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      a
#
# Licence:     MIT
#-------------------------------------------------------------------------------
from flask import Flask, render_template, request, redirect
import os
from pymongo import MongoClient

def connect():
    connection = MongoClient("localhost",27017)
    handle = connection["apitest1"]
    handle.authenticate("user","pw")
    return handle

app = Flask(__name__)
handle = connect()

#MAIN ROUTES
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/upsert", methods=['GET'])
def upsert():
    userinputs = [x for x in handle.trackingdb.find()]
    return render_template('upsert.html', userinputs=userinputs)

@app.route("/find", methods=['GET'])
def find():
    return render_template('find.html')

@app.route("/report", methods=['GET'])
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
def upsertwrite():
    form1 = {
            "assetid": request.form.get("asset"),
            "tagid": request.form.get("tag")
            }
    query = {"assetid": request.form.get("asset")}
    assetid = handle.trackingdb.update(query,{'$set': form1},**{'upsert':True})
    return redirect ("/upsert")

@app.route("/reportwrite", methods=['POST'])
def reportwrite():
    form1 = {
            "tagid": request.form.get("tag"),
            "readerid": request.form.get("reader")
            }
    query = {"tagid": request.form.get("tag")}
    assetid = handle.trackingdb.update(query,{"$set": form1},**{'upsert':True})
    return redirect ("/report")

@app.route("/deleteall", methods=['GET'])
def deleteall():
    handle.trackingdb.remove()
    return redirect ("/")

# Remove the "debug=True" for production
if __name__ == '__main__':
    app.run(debug=True)