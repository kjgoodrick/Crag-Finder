"""Contains the Coordinate Class

"""
from math import sqrt


class Coordinate:
    """A class for geographic coordinates

    Contains latitude and longitude and provides several helper methods for coordinate math and organization

    Parameters
    ----------
    lat : float
        The Coordinate's latitude
    lon : float
        The Coordinate's longitude
    """
    lat = 0
    lon = 0

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def __sub__(self, other: 'Coordinate') -> float:
        """Redefines the subtraction operator to find the distance between two points

        Distance is in degrees, so curvature of the earth does not need to be accounted for

        Parameters
        ----------
        other : Coordinate
            The other coordinate

        Returns
        -------
        distance : float
            The distance to the other coordinate

        """
        return sqrt((self.lat - other.lat)**2 + (self.lon - other.lon)**2)

    def __truediv__(self, other: 'Coordinate') -> 'Coordinate':
        """Redefines the division operator to find the middle point between two coordinates

        Parameters
        ----------
        other : Coordinate

        Returns
        -------
        mid_point : Coordinate
            The middle point of two coordinates

        """
        lat = (self.lat + other.lat) / 2
        lon = (self.lon + other.lon) / 2

        return Coordinate(lat, lon)

    @property
    def tuple(self):
        """A tuple of (Lat, Lon)

        Returns
        -------
        coordinate: tuple
            coordinate in tuple form: (Lat, Lon)
        """
        return self.lat, self.lon
