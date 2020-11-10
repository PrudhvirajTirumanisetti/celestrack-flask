'''
Created on Monday November 10, 2020

@author: Prudhviraj Tirumanisetti
'''
from flask import Flask, render_template, request, url_for, flash, redirect
from celestrack import ResourceFile, Compute_Satelite
import ephem

app = Flask(__name__)
MAXIMUM_RETENTION = 1
now = ephem.now()
Query = Compute_Satelite()


def file_retention():
    R = ResourceFile()
    if now - R.last_modified >= MAXIMUM_RETENTION:
        print("Retriving the latest data from the Celestrack data blog")
        R.fetch()
    else:
        print("Data is good")
    return

@app.route('/')
def index():
    file_retention()
    return render_template('index.html')

@app.route('/overhead', methods=('GET','POST'))
def overhead():
    file_retention()
    if request.method == 'GET':
        return render_template('overhead.html')
    if request.method == 'POST':
        City = request.form['City']
        Country = ''.join(str(request.form['Country']).split())
        UserDate = request.form['UserDate']
        return Query.over_head(City=City, Country=Country, User_Date=UserDate)

@app.route('/nextpass', methods=('GET','POST'))
def next_pass():
    file_retention()
    if request.method == 'GET':
        return render_template('nextpass.html')
    if request.method == 'POST':
        City = request.form['City']
        Country = ''.join(str(request.form['Country']).split())
        SateliteID = request.form['SateliteID']
        return Query.pass_next(City=City, Country=Country, SateliteID=SateliteID)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8900)
