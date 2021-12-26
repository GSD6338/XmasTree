import board
import neopixel
from ledsAdapters.LedsAdapter import LedsAdapter

class PhysicalLedsAdapter(LedsAdapter):
    def __init__(self, ledsCount):
        LedsAdapter.__init__(self, ledsCount)
        self._pixels = neopixel.NeoPixel(board.D18, ledsCount, auto_write=False)

    def showFrame(self, frame):
        ledsCounter = 0
        for color in frame:
            self.pixels[ledsCounter] = color
            ledsCounter += 1
