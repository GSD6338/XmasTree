# Based on code from https://github.com/standupmaths/xmastree2020

import board
import neopixel


def main():
    number_of_leds = 500
    pixels = neopixel.NeoPixel(board.D18, number_of_leds)

    for led in range(number_of_leds):
        pixels[led] = (0, 0, 0)

    print("Done")


if __name__ == '__main__':
    main()
