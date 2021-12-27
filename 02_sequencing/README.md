#Animation File Format

The animation files are CSV (comma separated value) spreadsheet files.

The first row contains the column names which are used to identify the contents of the column.
Every subsequent row contains the data for each frame.

The header names are:

`FRAME_ID` - This stores the index of the frame.
This column should contain integers.
Lowest values will be displayed first.
This column is optional. If undefined the frames will be displayed in the order they are in the CSV file. 

`FRAME_TIME` - The amount of time the frame will remain for.
This should contain floats eg 0.03333 is 1/30th of a second.
This column is optional. If undefined will default to 1/30th of a second.

`[RGB]_[0-9]+` - The intensity of each colour channel for the given LED index.
Examples are `R_0`, `G_0` and `B_0` which are the red, green and blue channel for LED 0.
The values of these columns should be floats or ints between 0 and 255 inclusive. 

⚠️Note that the old python running code has a number of limitations.
If you are getting errors running a CSV animation file with run.py make sure you have the latest version which removes all of these limitations.
