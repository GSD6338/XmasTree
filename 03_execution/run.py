# Based on code from https://github.com/standupmaths/xmastree2020
# Modified heavily by gentlegiantJGC

import argparse

import board
import neopixel

from run_utils import parse_animation_csv, draw_frames

# change if your setup has a different number of LEDs
NUMBER_OF_LEDS = 500


def load_and_run_csv(csv_path):
    frames, frame_times = parse_animation_csv(csv_path, NUMBER_OF_LEDS, "RGB")
    print("Finished Parsing")

    pixels = neopixel.NeoPixel(
        board.D18, NUMBER_OF_LEDS, auto_write=False, pixel_order=neopixel.RGB
    )

    # run the code on the tree
    while True:
        draw_frames(pixels, frames, frame_times)


def main():
    # parser to parse the command line inputs
    parser = argparse.ArgumentParser(description="Run a single spreadsheet on loop.")
    parser.add_argument(
        "csv_path",
        metavar="csv-path",
        type=str,
        help="The absolute or relative path to the csv file.",
    )

    args, _ = parser.parse_known_args()
    csv_path = args.csv_path
    load_and_run_csv(csv_path)


if __name__ == "__main__":
    main()
