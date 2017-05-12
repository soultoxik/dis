from observer import *

class Radar(Observer):
    def __init__(self, id, lat, lon, radius):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.radius = radius

    def isConfict(self, p0, p1):
        pass

    def onPublish(self, data):
        print(data)
