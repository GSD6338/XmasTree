# Based on code from https://github.com/standupmaths/xmastree2020
# Modified heavily by gentlegiantJGC

from typing import List
import os
import argparse

import board
import neopixel

from run_utils import parse_animation_csv, draw_frames, draw_lerp_frames, Sequence

NUMBER_OF_LEDS = 500


def run_folder(folder_path: str, loops_per_sequence: int, transition_frames: int):
    print(f"Sequences will loop {loops_per_sequence} times")
    print(f"Sequences will blend over {transition_frames} frames")

    print("Loading animation spreadsheets. This may take a while.")

    # Load and parse all the sequences at the beginning (it's a heavy process for the pi)
    csv_files: List[str] = []
    sequences: List[Sequence] = []
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        if file_name.endswith(".csv") and os.path.isfile(full_path):
            try:
                # try loading the spreadsheet and report any errors
                sequence = parse_animation_csv(full_path, NUMBER_OF_LEDS, "RGB")
            except Exception as e:
                print(f"Failed loading spreadsheet {file_name}.\n{e}")
            else:
                # if the spreadsheet successfully loaded then add it to the data
                sequences.append(sequence)
                csv_files.append(file_name)

    print("Finished loading animation spreadsheets.")

    # Init the neopixel
    pixels = neopixel.NeoPixel(
        board.D18, NUMBER_OF_LEDS, auto_write=False, pixel_order=neopixel.RGB
    )

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
