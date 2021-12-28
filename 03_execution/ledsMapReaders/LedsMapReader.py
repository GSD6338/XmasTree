class LedsMapReader():
    def __init__(self):
        self._leds = []
        
    def normalize(self):
        koef = 0
        for led in self._leds:
            if koef < abs(led[0]): koef = abs(led[0])
            if koef < abs(led[2]): koef = abs(led[2])
        
        for i in range(len(self._leds)):
            self._leds[i] = [self._leds[i][0]/koef, self._leds[i][1]/koef, self._leds[i][2]/koef]

    def getLed(self, index):
        return self._leds[index]
