# Based on code from https://github.com/standupmaths/xmastree2020

import time
import sys

import board
import neopixel


def main():
    number_of_leds = 500
    pixels = neopixel.NeoPixel(board.D18, number_of_leds)

    ids = sys.argv[1:]
    for led in ids:
        pixels[int(led)] = (255, 255, 255)
        time.sleep(1)

    print("Done")


if __name__ == '__main__':
    main()
