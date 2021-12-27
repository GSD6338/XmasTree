# Based on code from https://github.com/standupmaths/xmastree2020

from typing import List, Tuple, Optional
import time
import csv
import os
import argparse

import board
import neopixel

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
    return frames, frame_times


def draw_frame(pixels, frame, frame_time):
    t = time.time()
    for led in range(NUMBER_OF_LEDS):
        pixels[led] = frame[led]
    pixels.show()
    sleep_time = frame_time - (time.time() - t)
    if sleep_time > 0:
        time.sleep(sleep_time)


def draw_frames(pixels, frames, frame_times):
    """Draw a series of frames to the tree."""
    for frame, frame_time in zip(frames, frame_times):
        draw_frame(pixels, frame, frame_time)


def draw_lerp_frames(pixels, last_frame, next_frame, transition_frames):
    """Interpolate between two frames and draw the result."""
    for frame_index in range(1, transition_frames):
        ratio = frame_index / transition_frames
        draw_frame(
            pixels,
            [
                tuple(
                    round((1 - ratio) * channel_a + ratio * channel_b)
                    for channel_a, channel_b in zip(led_a, led_b)
                )
                for led, (led_a, led_b) in enumerate(zip(last_frame, next_frame))
            ],
            1 / 30,
        )


def run_folder(folder_path: str, loops_per_sequence: int, transition_frames: int):
    print(f"Sequences will loop {loops_per_sequence} times")
    print(f"Sequences will blend over {transition_frames} frames")

    print("Loading animation spreadsheets. This may take a while.")

    # Load and parse all the sequences at the beginning (it's a heavy process for the pi)
    csv_files = []
    sequences = []
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        if file_name.endswith(".csv") and os.path.isfile(full_path):
            try:
                # try loading the spreadsheet and report any errors
                sequence = parse_animation_csv(full_path)
            except Exception as e:
                print(f"Failed loading spreadsheet {file_name}.\n{e}")
            else:
                # if the spreadsheet successfully loaded then add it to the data
                sequences.append(sequence)
                csv_files.append(file_name)

    print("Finished loading animation spreadsheets.")

    # Init the neopixel
    pixels = neopixel.NeoPixel(board.D18, NUMBER_OF_LEDS, auto_write=False)

    last_frame = None

    # Play all sequences in a loop
    while True:
        # iterate over the sequences
        for sequence_id, (file_name, (frames, frame_times)) in enumerate(
            zip(csv_files, sequences)
        ):
            print(f"Playing file {file_name}")
            for loop in range(0, loops_per_sequence):
                # run this bit as many as was requested
                if (
                    last_frame is not None
                    and frames
                    and any(
                        # if any of the colour channels are greater than 20 points different then lerp between them.
                        abs(channel_b - channel_a) > 20
                        for led_a, led_b in zip(last_frame, frames[0])
                        for channel_a, channel_b in zip(led_a, led_b)
                    )
                ):
                    # if an animation has played and the last and first frames are different enough
                    # then interpolate from the last state to the first state
                    # Some animations may be designed to loop so adding a fade will look weird
                    draw_lerp_frames(pixels, last_frame, frames[0], transition_frames)

                print(f"Loop {loop + 1} of {loops_per_sequence}")

                # push all the frames to the tree
                draw_frames(pixels, frames, frame_times)

                # Store the last frame if it exists
                if frames:
                    last_frame = frames[-1]


def main():
    # parser to parse the command line inputs
    parser = argparse.ArgumentParser(description="Run all spreadsheet in a directory.")
    parser.add_argument(
        "csv_directory",
        metavar="csv-directory",
        type=str,
        help="The absolute or relative path to a directory containing csv files.",
    )
    parser.add_argument(
        "loops_per_sequence",
        type=int,
        nargs="?",
        default=5,
        help="The number of times each sequence loops. Default is 5.",
    )
    parser.add_argument(
        "transition_frames",
        type=int,
        nargs="?",
        default=15,
        help="The number of frames (at 30fps) over which to transition between sequences. "
        "Set to 0 to disable interpolation.",
    )
    args, _ = parser.parse_known_args()
    run_folder(args.csv_directory, args.loops_per_sequence, args.transition_frames)


if __name__ == "__main__":
    main()
