from math import sqrt


class Coordinate:
    lat = 0
    lon = 0

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __sub__(self, other):
        return sqrt((self.lat - other.lat)**2 + (self.lon - other.lon)**2)

    def __truediv__(self, other):
        lat = (self.lat + other.lat) / 2
        lon = (self.lon + other.lon) / 2

        return Coordinate(lat, lon)

    @property
    def tuple(self):
        return self.lat, self.lon
