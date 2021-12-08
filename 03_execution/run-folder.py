# Based on code from https://github.com/standupmaths/xmastree2020

import board
import neopixel
import time 
from csv import reader
import sys
import os

# sleep_time = 0.033 # approx 30fps 
sleep_time = 0.017  # approx 60fps
NUMBEROFLEDS = 500
LOOPS_PER_SEQUENCE = 5
TRANSITION_FRAMES = 60

if len(sys.argv) > 2:
    LOOPS_PER_SEQUENCE = int(sys.argv[2])
if len(sys.argv) > 3:
    TRANSITION_FRAMES  = int(sys.argv[3])

print("Sequences will loop " + str(LOOPS_PER_SEQUENCE) + " times")
print("Sequences will blend over " + str(TRANSITION_FRAMES) + " frames")





# helper function for chunking 
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]
        
# Given two light frames and a tween ratio, returns an interpolated one
def tween_frames(frame_a, frame_b, ratio):
    # sanity
    len_a = len(frame_a)
    len_b = len(frame_b)
    if len_a != len_b:
        print("cannot interpolate frames with different lengths")
        return frame_a

    tween = []
    for i in range(0, len_a):
        g = round((1 - ratio) * frame_a[i][0] + ratio * frame_b[i][0])
        r = round((1 - ratio) * frame_a[i][1] + ratio * frame_b[i][1])
        b = round((1 - ratio) * frame_a[i][2] + ratio * frame_b[i][2])
        tween.append((g, r, b))  # remember that LEDs take GRB values

    return tween

# Given two sequences, returns the second one with the staring block 
# blended with the end of the first one
def blend_lights(lights_a, lights_b, transition_length):
    # Blend the last and first blocks of lights
    end_a = lights_a[len(lights_a) - transition_length:]
    # print(str(len(end_a)))
    start_b = lights_b[:transition_length]
    # print(str(len(start_b)))

    blend = []
    step = 1.0 / (transition_length + 1)
    for i in range(0, transition_length):
        n = step * (i + 1)
        frame = tween_frames(end_a[i], start_b[i], n)
        blend.append(frame)
    
    return blend + lights_b[transition_length:]



# Given a filename, returns the parsed light object
def getLights(csvFile):
    print("Parsing " + csvFile)
    # read the file
    # iterate through the entire thing and make all the points the same colour 
    lightArray = []
    
    with open(csvFile, 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)

        # Iterate over each row in the csv using reader object
        lineNumber = 0
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            # break up the list of rgb values 
            # remove the first item
            if lineNumber > 0:
                parsed_row = []
                row.pop(0)
                chunked_list = list(chunks(row, 3))
                for element_num in range(len(chunked_list)):
                    # this is a single light 
                    r = float(chunked_list[element_num][0])
                    g = float(chunked_list[element_num][1])
                    b = float(chunked_list[element_num][2])
                    light_val = (g, r, b)  # these LED lights take GRB color for some reason!
                    # turn that led on
                    parsed_row.append(light_val)
                
                # append that line to lightArray 
                lightArray.append(parsed_row)
            
            lineNumber += 1

    #print("Finished Parsing file " + csvFile)
    
    return lightArray


# Given a light sequence, it plays it on the tree
def playLights(neop, lights):
    f = 0
    for frame in lights:
        LED = 0
        while LED < NUMBEROFLEDS:
            neop[LED] = frame[LED]
            LED += 1
        neop.show()
        f += 1




# Init the neopixel
pixels = neopixel.NeoPixel(board.D18, NUMBEROFLEDS, auto_write=False)

# get foldername from CLI arguments
folder_path = sys.argv[1]

# load csv files
csv_files = []
for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        csv_files.append(file)


# Parse all the sequences at the beginning (its a heavy process for the pi)
sequences = []
for file in csv_files:
    full_path = os.path.join(folder_path, file)
    if os.path.isfile(full_path):
        lights = getLights(full_path)
        sequences.append(lights)

# Play sequences in a loop
while True:
    id = 0
    for lights in sequences:
        prev = sequences[id - 1]
        print("Playing file " + csv_files[id])
        for i in range(0, LOOPS_PER_SEQUENCE):
            lights_now = []
            if i != (LOOPS_PER_SEQUENCE - 1):
                print("Loop " + str(i + 1) + " from " + str(LOOPS_PER_SEQUENCE), end='\r')
                if i == 0:
                    lights_now = blend_lights(prev, lights, TRANSITION_FRAMES)
                else:
                    lights_now = lights
            else:
                print("Loop " + str(i + 1) + " from " + str(LOOPS_PER_SEQUENCE))
                lights_now = lights[:len(lights)-TRANSITION_FRAMES]
            
            playLights(pixels, lights_now)

        id += 1
