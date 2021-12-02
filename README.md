# Computational Xmas Tree

This repo contains the code for the computational illumination of a Christmas Tree! 

It is based on the work by Matt Parker from @standupmaths, and his video ["I wired my tree with 500 LED lights and calculated their 3D coordinates"](https://www.youtube.com/watch?v=TvlpIojusBE). 

This version contains an independent LED 3D calibration routine based on Matt's explanations on the video developed by @range_et, Grasshopper + C# scripts to generate CSVs with animated light sequences developed by @garciadelcastillo, and python scripts for the Raspberry Pi to load and run the CSV files on the tree. 

## Usage

### Calibration
1. Run `imageCapture.py` from a Raspberry Pi with a webcam and connected to the tree. The script will take one image per LED for angle 0.
2. Repeat this process by physically rotating the tree 45, 90, 135, 180, 225, 270 & 315 degrees, and correspondingly updating the `MASTERDIR` variable in the script.
3. Run `mapper.ipynb` to process all the images and generate the coordinates of the tree. This may take some time! 
4. Run `adjuster.ipynb` to correct some of the outliers. 

A version of the final outcome from our test tree is provided in file `coords_norm_adjusted_new.txt`. If you don't have a tree yourself, feel free to use these as the starting point. 

Questions, suggestions and PRs can be directed to @range_et! 

