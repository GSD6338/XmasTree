import board
import neopixel
import time 
from csv import reader

sleepTime = 0.1
NUMBEROFLEDS = 5
pixels = neopixel.NeoPixel(board.D18, NUMBEROFLEDS, auto_write=False)
csvFile = "/home/pi/Desktop/test.csv"
# read the file
# iterate through the entire thing and make all the points the same colour 
with open(csvFile, 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    # Iterate over each row in the csv using reader object
    while True:
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            for x in range(NUMBEROFLEDS):
                pixels[0] = row[x]
            time.sleep(sleepTime)


