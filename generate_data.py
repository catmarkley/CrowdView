#!/usr/bin/env python3

import math
import random

# Define number of data points
# 6048 is 3 weeks of data
DATA_POINTS = 6048
PI = 3.145926
locations = ["NDH", "SDH", "Hes", "Smiths"]

# Every 1260 data points describes a week
# Every 180 data points describes a day
# Every 12 data points describes an hour
# Military time will be used

# Open file
file = open("data_generated.csv", "w")

for loc in locations[0:-1]:
    loc = loc + ","
    file.write(loc)

file.write(locations[-1])
file.write("\n")


for i in range(DATA_POINTS):
    # split into hours
    x = (i % 288)/12

    # Add data to csv
    for loc in locations[0:-1]:
        # generate data
        if (loc == "NDH" or loc == "SDH"):
            data = 0.9*(math.sin(1.25*x-9.4-1.5*PI)+1)/2
        else:
            data = 0.9*(math.sin(0.9*x - PI)+1)/2

        # Randomize data a bit
        rando = random.gauss(0.1, 0.05)
        data = data + rando
        if data > 1:
            data = 1
        if data < 0:
            data = 0

        # Add to file
        data_str = str(data) + ","
        file.write(data_str)

    # generate data
    if (loc == "NDH" or loc == "SDH"):
        data = 0.9*(math.sin(1.25*x-9.4-1.5*PI)+1)/2
    else:
        data = 0.9*(math.sin(0.9*x - PI)+1)/2

    # Randomize data a bit
    rando = random.gauss(0.1, 0.05)
    data = data + rando
    if data > 1:
        data = 1
    if data < 0:
        data = 0
    # Add to file
    data_str = str(data) + "\n"
    file.write(data_str)
