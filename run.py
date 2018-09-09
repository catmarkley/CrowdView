#! /usr/bin/python
from flask import Flask, flash, redirect, render_template, request, session, abort
from random import randint
import time
import math
import json
import datetime

app = Flask(__name__)

colors = []
crowds = []
occupancy = []
averages = []
date = "N/A"

MAX_NDH = 750
MAX_SDH = 750
MAX_Hes = 1000
MAX_Smiths = 250

NDH_color = '#5cff00'
SDH_color = '#5cff00'
Smiths_color = '#5cff00'
Hes_color = '#5cff00'

# Starting day
START_DAY = 5 # we will change this to a date (such as 16, for January 16th)
# Starting hour
START_HOUR = 7 # 7 a.m.
# Ending hour - probably won't use
END_HOUR = 22 - START_HOUR # 10 p.m.
# Starting minute
START_MIN = 0 # we probably won't use this since it should stay at 0
# Ending minute - probably won't use
END_MIN = 55

@app.route("/<string:name>")
def hello(name):
    return render_template('hello.html', **locals())

@app.route("/")
def index():
    NDH = []
    SDH = []
    Hes = []
    Smiths = []

    dataSetup(NDH, SDH, Hes, Smiths)
    temp = getRandomInt()

    d = datetime.datetime.now()
    day_in = d.day
    hour_in = d.hour-12
    min_in = d.minute
    maximums = [MAX_NDH, MAX_SDH, MAX_Hes, MAX_Smiths]
    crowds = [0,0,0,0]
    averages = [0,0,0,0]
    colors = [NDH_color, SDH_color, Smiths_color, Hes_color]
    index = 0
    date = "N/A"

    generateCrowds(min_in, hour_in, day_in, crowds, NDH, SDH, Hes, Smiths, index)
    generateAverages(index, averages, NDH, SDH, Hes, Smiths)
    generateColors(min_in, hour_in, day_in, date, colors, averages, crowds)

    return render_template('index.html', **locals())

def getRandomInt():
    return randint(0,10)

@app.route("/refresh")
def refresh():
    temp = "yeeeeeee"
    return render_template('index.html', **locals())

def dataSetup(NDH, SDH, Hes, Smiths):
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

def generateCrowds(min_in, hour_in, day_in, crowds, NDH, SDH, Hes, Smiths, index):
    # The day will be converted to a day in the year between 0-355
    closed = False # This variable is set to true if the time is outside of the daily hours

    # Get input time
    min_in += 1 # assuming an integer, but input data will probably have to be parsed and typecasted
    if (min_in > 60):
        min_in = 0
        hour_in += 1

    if (not hour_in % 24):
        day_in += 1

    # --------------------------------------------------------------------------- #
    # Convert the time numbers to an index

    min = math.floor(min_in/5) + START_MIN # produces mintues between 0 and 11 (mapping to minutes 0 to 55)
    print("Min: ", min)

    hour = math.floor(hour_in)
    print("Hour: ", hour)

    if(hour < START_HOUR or hour >= END_HOUR):
        closed = True

    day = math.floor(day_in) - START_DAY # Note the subtraction of the start day here
    print("Day: ", day)

    if(day < 0):
        day = 0

    index = int(day*288 + hour*12 + min)

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

    print("Current NDH crowd: ", NDH_crowd)

    crowds[0] = NDH_crowd
    crowds[1] = SDH_crowd
    crowds[2] = Hes_crowd
    crowds[3] = Smiths_crowd

def generateAverages(index, averages, NDH, SDH, Hes, Smiths):
    # --------------------------------------------------------------------------- #
    # Create a predicting mechanism

    # The day will be converted to a day in the year between 0-355
    closed = False # This variable is set to true if the time is outside of the daily hours

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

        # DATA POINT BEHIND
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
        
    averages[0] = NDH_average
    averages[1] = SDH_average
    averages[2] = Hes_average
    averages[3] = Smiths_average

def generateColors(min_in, hour_in, day_in, date, colors, averages, crowds):

    NDH_crowd = crowds[0]
    SDH_crowd = crowds[1]
    Hes_crowd = crowds[2]
    Smiths_crowd = crowds[3]

    NDH_average = averages[0]
    SDH_average = averages[1]
    Hes_average = averages[2]
    Smiths_average = averages[3]

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
    min_str = '{:0>2}'.format(min_in*5)
    date = "September "+ str(day_in)
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

    colors[0] = NDH_color
    colors[0] = SDH_color
    colors[0] = Hes_color
    colors[0] = Smiths_color

if __name__ == "__main__":
	app.run()