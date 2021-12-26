import json
from ledsMapReaders.LedsMapReader import LedsMapReader


class TxtLedsMapReader(LedsMapReader):
    def __init__(self, filePath):
        LedsMapReader.__init__(self)
        ledsData = open(filePath, mode='r', encoding='utf-8-sig')
        for ledRow in ledsData:
            ledCoords = json.loads(ledRow)
            self._leds.append([float(ledCoords[0]), float(ledCoords[2]), float(ledCoords[1])])
