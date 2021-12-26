# Based on code from https://github.com/standupmaths/xmastree2020

import time
import sys

from animationFileReaders.CsvAnimationFileReader import CsvAnimationFileReader


class Tree():
    def __init__(self, ledsAdapter):
        self._ledsAdapter = ledsAdapter

    def runRepeatedAnimation(self, animationFileReader, repeats = 0, frameRate = 60):
        repeatCounter = 0;
        while (repeatCounter < repeats) or (repeats == 0):
            animationFileReader.resetAnimation()
            self.runAnimation(animationFileReader, frameRate)
            repeatCounter += 1
        self.flushLeds()

    def runAnimation(self, animationFileReader, frameRate = 60):
        while True:
            frame = animationFileReader.getFrame()
            self._ledsAdapter.showFrame(frame)
            time.sleep(1/frameRate)
            if (not animationFileReader.nextFrame()): break

    def flushLeds(self):
        self._ledsAdapter.flush()


# if LEDs map file is set then select map reader by extension and configure Visual LEDs adapter
if len(sys.argv) > 2:
    mapFileName = sys.argv[2]
    mapFileNameExtension = mapFileName.split(".")[-1]
    if (mapFileNameExtension == 'txt'):
        TxtLedsMapReaderModule = __import__('ledsMapReaders.TxtLedsMapReader')
        TxtLedsMapReader = getattr(TxtLedsMapReaderModule, 'TxtLedsMapReader')
        mapReader = TxtLedsMapReader.TxtLedsMapReader(mapFileName)
    elif (mapFileNameExtension == 'csv'):
        CsvLedsMapReaderModule = __import__('ledsMapReaders.CsvLedsMapReader')
        CsvLedsMapReader = getattr(CsvLedsMapReaderModule, 'CsvLedsMapReader')
        mapReader = CsvLedsMapReader.CsvLedsMapReader(mapFileName)
    else:
        print('Unknown LED map type')
        quit()

    VisualLedsAdapterModule = __import__('ledsAdapters.VisualLedsAdapter')
    VisualLedsAdapter = getattr(VisualLedsAdapterModule, 'VisualLedsAdapter')
    ledsAdapter = VisualLedsAdapter.VisualLedsAdapter(500, mapReader, 800, 800)
# if LEDs file isn't set then configure Physical LEDs adapter
else:
    PhysicalLedsAdapterModule = __import__('ledsAdapters.PhysicalLedsAdapter')
    PhysicalLedsAdapter = getattr(PhysicalLedsAdapterModule, 'PhysicalLedsAdapter')
    ledsAdapter = PhysicalLedsAdapter.PhysicalLedsAdapter(500)
    
mapReader.normalize()

tree = Tree(ledsAdapter)
tree.runRepeatedAnimation(CsvAnimationFileReader(sys.argv[1]), 0, 60)
