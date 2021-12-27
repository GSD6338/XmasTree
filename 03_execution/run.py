# Based on code from https://github.com/standupmaths/xmastree2020

from typing import List, Tuple, Optional
import time
import csv
import argparse

import board
import neopixel

# change if your setup has a different number of LEDs
NUMBER_OF_LEDS = 500


def parse_animation_csv(
    csv_path,
) -> Tuple[List[List[Tuple[float, float, float]]], List[float]]:
    """
    Parse a CSV animation file into python objects.

    :param csv_path: The path to the csv animation file
    :return: A list LED colours per frame (GRB) and a list of times for each frame
    """
    # parse the CSV file
    # The example files in this repository start with \xEF\xBB\xBF See UTF-8 BOM
    # If read normally these become part of the first header name
    # utf-8-sig reads this correctly and also handles the case when they don't exist
    with open(csv_path, "r", encoding="utf-8-sig") as csv_file:
        # pass the file object to reader() to get the reader object
        csv_reader = csv.reader(csv_file)

        # this is a list of strings containing the column names
        header = next(csv_reader)

        # read in the remaining data
        data = list(csv_reader)

    # create a dictionary mapping the header name to the index of the header
    header_indexes = dict(zip(header, range(len(header))))

    # find the column numbers of each required header
    # we should not assume that the columns are in a known order. Isn't that the point of column names?
    # If a column does not exist it is set to None which is handled at the bottom and populates the column with 0.0
    led_columns: List[Tuple[Optional[int], Optional[int], Optional[int]]] = [
        tuple(header_indexes.pop(f"{channel}_{led_index}", None) for channel in "GRB")
        for led_index in range(NUMBER_OF_LEDS)
    ]

    if "FRAME_ID" in header_indexes:
        # get the frame id column index
        frame_id_column = header_indexes.pop("FRAME_ID")
        # don't assume that the frames are in chronological order. Isn't that the point of storing the frame index?
        # sort the frames by the frame index
        data = sorted(data, key=lambda frame_data: int(frame_data[frame_id_column]))
        # There may be a case where a frame is missed eg 1, 2, 4, 5, ...
        # Should we duplicate frame 2 in this case?
        # For now it can go straight from frame 2 to 4

    if "FRAME_TIME" in header_indexes:
        # Add the ability for the CSV file to specify how long the frame should remain for
        # This will allow users to customise the frame rate and even have variable frame rates
        # Note that frame rate is hardware limited because the method that pushes changes to the tree takes a while.
        frame_time_column = header_indexes.pop("FRAME_TIME")
        frame_times = [float(frame_data[frame_time_column]) for frame_data in data]
    else:
        # if the frame time column is not defined then run as fast as possible like the old code.
        frame_times = [0] * len(data)

    frames = [
        [
            tuple(
                # Get the LED value or populate with 0.0 if the column did not exist
                0.0 if channel is None else float(frame_data[channel])
                # for each channel in the LED
                for channel in channels
            )
            # for each LED in the chain
            for channels in led_columns
        ]
        # for each frame in the data
        for frame_data in data
    ]
    print("Finished Parsing")
    return frames, frame_times


def load_and_run_csv(csv_path):
    frames, frame_times = parse_animation_csv(csv_path)

    pixels = neopixel.NeoPixel(board.D18, NUMBER_OF_LEDS, auto_write=False)

    # run the code on the tree
    while True:
        for frame_index, (frame, frame_time) in enumerate(zip(frames, frame_times)):
            t = time.time()
            print(f"running frame {frame_index}")
            for led in range(NUMBER_OF_LEDS):
                pixels[led] = frame[led]
            pixels.show()
            sleep_time = frame_time - (time.time() - t)
            if sleep_time > 0:
                time.sleep(sleep_time)


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
