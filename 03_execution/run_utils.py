# Written by gentlegiantJGC

from typing import Tuple, List, Optional, NamedTuple
import csv
import time

import neopixel

Color = Tuple[float, float, float]
Frame = List[Color]
Frames = List[Frame]
FrameTime = float
FrameTimes = List[FrameTime]
Sequence = NamedTuple("Sequence", [("frames", Frames), ("frame_times", FrameTimes)])


def parse_animation_csv(
    csv_path: str, number_of_leds: int, channel_order="RGB"
) -> Sequence:
    """
    Parse a CSV animation file into python objects.

    :param csv_path: The path to the csv animation file
    :param number_of_leds: The number of LEDs that the device supports
    :param channel_order: The order the channels should be loaded. Must be "RGB" or "GRB"
    :return: A Sequence namedtuple containing frame data  and frame times
    """
    if channel_order not in ("RGB", "GRB"):
        raise ValueError(f"Unsupported channel order {channel_order}")
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
        tuple(
            header_indexes.pop(f"{channel}_{led_index}", None)
            for channel in channel_order
        )
        for led_index in range(number_of_leds)
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
        frame_times = [float(frame_data[frame_time_column])/1000 for frame_data in data]
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
    return Sequence(frames, frame_times)


def draw_frame(pixels: neopixel.NeoPixel, frame: Frame, frame_time: float):
    """
    Draw a single frame and wait to make up the frame time if required.

    :param pixels: The neopixel interface
    :param frame: The frame to draw
    :param frame_time: The time this frame should remain on the device
    """
    t = time.perf_counter()
    for led in range(pixels.n):
        pixels[led] = frame[led]
    pixels.show()
    end_time = t + frame_time
    while time.perf_counter() < end_time:
        time.sleep(0)


def draw_frames(pixels: neopixel.NeoPixel, frames: Frames, frame_times: FrameTimes):
    """
    Draw a series of frames to the tree.

    :param pixels: The neopixel interface
    :param frames: The frames to draw
    :param frame_times: The frame time for each frame
    """
    for frame, frame_time in zip(frames, frame_times):
        draw_frame(pixels, frame, frame_time)


def draw_lerp_frames(
    pixels: neopixel.NeoPixel,
    last_frame: Frame,
    next_frame: Frame,
    transition_frames: int,
):
    """
    Interpolate between two frames and draw the result.

    :param pixels: The neopixel interface
    :param last_frame: The start frame
    :param next_frame: The end frame
    :param transition_frames: The number of frames to take to fade
    """
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
