class LedsAdapter():
    def __init__(self, ledsCount):
        self._ledsCount = ledsCount

    def showFrame(self, frame):
        pass

    def flush(self):
        self.showFrame([(0, 0, 0) for x in range(self._ledsCount)])
