from csv import reader
from ledsMapReaders.LedsMapReader import LedsMapReader


class CsvLedsMapReader(LedsMapReader):
    def __init__(self, filePath):
        LedsMapReader.__init__(self)
        csvReader = reader(open(filePath, mode='r', encoding='utf-8-sig'))
        for ledCoords in csvReader:
            try:
                float(ledCoords[0])
            except ValueError:
                continue
            if (len(ledCoords) == 4): ledCoords.pop(0)
            self._leds.append([float(ledCoords[0]), float(ledCoords[2]), float(ledCoords[1])])
