#! /usr/bin/python
from flask import Flask, flash, redirect, render_template, request, session, abort
from random import randint
import time
import math
import json
import datetime

app = Flask(__name__)

NDH = []
SDH = []
Hes = []
Smiths = []

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/<string:name>/")
def index(name):
    dataSetup()
    temp = NDH[4]
    return render_template('test.html', **locals())

def getRandomInt():
    return randint(0,10)

@app.route("/refresh")
def refresh():
    temp = "yeeeeeee"
    return render_template('test.html', **locals())

def dataSetup():
    # Open the data and turn it into a list
    file = open('data_generated.csv').read()

    data = file.split('\n')
    for row in range(1, len(data) - 1):
        temp = data[row].split(',')
        NDH.append(temp[0])
        SDH.append(temp[1])
        Hes.append(temp[2])
        Smiths.append(temp[3])

    # Edit the data to be between 0 and MAX instead of a decimal between -1 and 1

    MAX_NDH = 750
    MAX_SDH = 750
    MAX_Hes = 1000
    MAX_Smiths = 250

    for i in range(0, len(NDH)):
        NDH[i] = int(math.floor(float(NDH[i])*MAX_NDH/2 + MAX_NDH/2))
        SDH[i] = int(math.floor(float(SDH[i])*MAX_SDH/2 + MAX_SDH/2))
        Hes[i] = int(math.floor(float(Hes[i])*MAX_Hes/2 + MAX_Hes/2))
        Smiths[i] = int(math.floor(float(Smiths[i])*MAX_Smiths/2 + MAX_Smiths/2))

if __name__ == "__main__":
	app.run()
