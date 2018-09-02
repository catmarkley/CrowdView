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
colors = []
crowds = []
occupancy = []
averages = []
date = "N/A"

# Starting day
START_DAY = 0 # we will change this to a date (such as 16, for January 16th)
# Starting hour
START_HOUR = 7 # 7 a.m.
# Ending hour - probably won't use
END_HOUR = 22 - START_HOUR # 10 p.m.
# Starting minute
START_MIN = 0 # we probably won't use this since it should stay at 0
# Ending minute - probably won't use
END_MIN = 55

# starting time

d = datetime.datetime.now()

day_in = d.day
hour_in = d.hour-5
min_in = d.minute

START_DAY = day_in - 3

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/<string:name>/")
def index(name):
    dataSetup()
    temp = getRandomInt()

    NDH_crowd = 100
    SDH_crowd = 101
    Hes_crowd = 102
    Smiths_crowd = 103

    MAX_NDH = 200
    MAX_SDH = 201
    MAX_Hes = 202
    MAX_Smiths = 203

    NDH_average = 150
    SDH_average = 151
    Hes_average = 152
    Smiths_average = 153

    NDH_color = '#5cff00'
    SDH_color = '#5cff00'
    Smiths_color = '#5cff00'
    Hes_color = '#5cff00'

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

def newEntry():
    dataSetup()

    # Get input time
    min_in += 1 # assuming an integer, but input data will probably have to be parsed and typecasted
    if (min_in > 60):
        min_in = 0
        hour_in += 1

    if (not hour_in % 24):
        day_in += 1

    # The day will be converted to a day in the year between 0-355
    closed = False # This variable is set to true if the time is outside of the daily hours

    # --------------------------------------------------------------------------- #
    # Convert the time numbers to an index

    min = math.floor(min_in/5) + START_MIN # produces mintues between 0 and 11 (mapping to minutes 0 to 55)

    hour = math.floor(hour_in)

    if(hour < START_HOUR or hour >= END_HOUR):
        closed = True

    day = math.floor(day_in) - START_DAY # Note the subtraction of the start day here

    if(day < 0):
        day = 0

    index = day*288 + hour*12 + min

    # --------------------------------------------------------------------------- #
    # Retrieve current crowd
    if(closed):
        NDH_crowd = 0
        SDH_crowd = 0
        Hes_crowd = 0
        Smiths_crowd = 0
    else:
        NDH_crowd = NDH[index]
        SDH_crowd = SDH[index]
        Hes_crowd = Hes[index]
        Smiths_crowd = Smiths[index]

    # --------------------------------------------------------------------------- #
    # Create a predicting mechanism

    # 15 range - predicts based on the surrounding 15 minutes in past days
    loop_index = index
    first = True
    n = 0

    total_NDH = 0
    total_SDH = 0
    total_Hes = 0
    total_Smiths = 0

    while (loop_index > 0) and (not closed):
        # DATA POINT IN FRONT
        if(first == False and hour < END_HOUR):
            total_NDH += NDH[loop_index+1]
            total_SDH += SDH[loop_index+1]
            total_Hes += Hes[loop_index+1]
            total_Smiths += Smiths[loop_index+1]
            n += 1
        else:
            first = False

        # DATA POINT AT CURRENT POSITION
        total_NDH += NDH[loop_index]
        total_SDH += SDH[loop_index]
        total_Hes += Hes[loop_index]
        total_Smiths += Smiths[loop_index]
        n += 1

        # DATA POINT BEHINDs
        if(hour > START_HOUR):
            total_NDH += NDH[loop_index-1]
            total_SDH += SDH[loop_index-1]
            total_Hes += Hes[loop_index-1]
            total_Smiths += Smiths[loop_index-1]
            n += 1

        loop_index -= 288 # There are 288 data points in a day

    # Checking if there is a past average (aka that it is not day 0)
    if(n != 0):
        NDH_average = total_NDH/n
        SDH_average = total_SDH/n
        Hes_average = total_Hes/n
        Smiths_average = total_Smiths/n
    else:
        if(not closed):
            NDH_average = NDH[index]
            SDH_average = SDH[index]
            Hes_average = Hes[index]
            Smiths_average = Smiths[index]
        else:
            NDH_average = 0
            SDH_average = 0
            Hes_average = 0
            Smiths_average = 0

    # Makes sure there is a crowd and average exists
    if(NDH_average != 0 and NDH_crowd != 0):
        NDH_ratio = NDH_crowd/NDH_average # this ratio will determine the color
        SDH_ratio = SDH_crowd/SDH_average
        Hes_ratio = Hes_crowd/Hes_average
        Smiths_ratio = Smiths_crowd/Smiths_average
    else:
        NDH_ratio = 1
        SDH_ratio = 1
        Hes_ratio = 1
        Smiths_ratio = 1


    # --------------------------------------------------------------------------- #
    # Generate the color for each place
    rg_scale = [
            '#FF0000',
            '#FF1100',
            '#FF2200',
            '#FF3300',
            '#FF4400',
            '#FF5500',
            '#FF6600',
            '#FF7700',
            '#FF8800',
            '#FF9900',
            '#FFAA00',
            '#FFBB00',
            '#FFCC00',
            '#FFDD00',
            '#FFEE00',
            '#FFFF00',
            '#EEFF00',
            '#99FF00',
            '#DDFF00',
            '#BBFF00',
            '#CCFF00',
            '#AAFF00',
            '#77FF00',
            '#88FF00',
            '#66FF00',
            '#55FF00',
            '#44FF00',
            '#33FF00',
            '#22FF00',
            '#11FF00',
            '#00FF00'
            ]

    NDH_red = 255
    NDH_green = 255
    SDH_red = 255
    SDH_green = 255
    Hes_red = 255
    Hes_green = 255
    Smiths_red = 255
    Smiths_green = 255
    blue = 00

    factor = 20 # Determines the spread of the generated color

    if(NDH_ratio < 1):
        diff = 1 - NDH_ratio
        NDH_red = math.floor(NDH_red*diff*factor)
    if(NDH_ratio > 1):
        diff = NDH_ratio - 1
        NDH_green = math.floor(NDH_green*diff*factor)

    if(SDH_ratio < 1):
        diff = 1 - SDH_ratio
        SDH_red = math.floor(SDH_red*diff*factor)
    if(SDH_ratio > 1):
        diff = SDH_ratio - 1
        SDH_green = math.floor(SDH_green*diff*factor)

    if(Hes_ratio < 1):
        diff = 1 - Hes_ratio
        Hes_red = math.floor(Hes_red*diff*factor)
    if(Hes_ratio > 1):
        diff = Hes_ratio - 1
        Hes_green = math.floor(Hes_green*diff*factor)

    if(Smiths_ratio < 1):
        diff = 1 - Smiths_ratio
        Smiths_red = math.floor(Smiths_red*diff*factor)
    if(Smiths_ratio > 1):
        diff = Smiths_ratio - 1
        Smiths_green = math.floor(Smiths_green*diff*factor)

    color_list = [NDH_red, NDH_green, SDH_red, SDH_green, Hes_red, Hes_green, Smiths_red, Smiths_green]

    for i in range(0, len(color_list)):
        if(color_list[i] < 16):
            color_list[i] = 16
        elif(color_list[i] > 255):
            color_list[i] = 255
        color_list[i] = str(hex(color_list[i]))
        color_list[i] = color_list[i][2] + color_list[i][3]

    NDH_color = "#" + color_list[0] + color_list[1] + "00"
    SDH_color = "#" + color_list[2] + color_list[3] + "00"
    Hes_color = "#" + color_list[4] + color_list[5] + "00"
    Smiths_color = "#" + color_list[6] + color_list[7] + "00"

    # Make Date String
    hour_str = '{:0>2}'.format(hour_in)
    min_str = '{:0>2}'.format(min*5)
    date = "March "+ str(day_in)
    # print(day)
    # print(day % 10)
    if(day_in % 10 == 1):
        date += "st"
    elif(day_in % 10 == 2):
        date += "nd"
    elif(day_in % 10 == 3):
        date += "rd"
    else:
        date += "th"

    date += " " + hour_str + ":" + min_str

    colors = [NDH_color,SDH_color,Hes_color,Smiths_color]
    crowds = [NDH_crowd,SDH_crowd,Hes_crowd,Smiths_crowd]
    occupancy = [MAX_NDH,MAX_SDH,MAX_Hes,MAX_Smiths]
    averages = [NDH_average,SDH_average,Hes_average,Smiths_average]

    temp = getRandomInt()

    return render_template('test.html', **locals())

if __name__ == "__main__":
	app.run()
