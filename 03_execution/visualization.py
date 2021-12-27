# Based on code from https://github.com/standupmaths/xmastree2020

import time
import sys

from animationFileReaders.CsvAnimationFileReader import CsvAnimationFileReader
from ledsAdapters.VisualLedsAdapter import VisualLedsAdapter


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

    ledsAdapter = VisualLedsAdapter(500, mapReader, 800, 800)
    
mapReader.normalize()

tree = Tree(ledsAdapter)
tree.runRepeatedAnimation(CsvAnimationFileReader(sys.argv[1]), 0, 60)
