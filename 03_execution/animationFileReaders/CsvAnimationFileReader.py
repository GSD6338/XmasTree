from csv import reader
from animationFileReaders.AnimationFileReader import AnimationFileReader


class CsvAnimationFileReader(AnimationFileReader):
    def __init__(self, filePath):
        AnimationFileReader.__init__(self)
        self._filePath = filePath
        self._file = None
        self._fileReader = None
        self._frame = None
        self.resetAnimation()

    def resetAnimation(self):
        if (self._file != None):
            self._file.close()
        self._file = open(self._filePath, 'r')
        self._fileReader = reader(self._file)
        self.nextFrame()
        self.nextFrame()

    def nextFrame(self):
        row = next(self._fileReader, None)
        if (row == None): return False
        row.pop(0)
        self._frame = [(row[pixelNumber], row[pixelNumber+1], row[pixelNumber+2]) for pixelNumber in range(0, len(row), 3)]
        return True

    def getFrame(self):
        return self._frame

