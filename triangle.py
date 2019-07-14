from typing import List
from coordinate import Coordinate
from math import sqrt
import numpy as np
import miniball
from geopy.distance import distance
from itertools import combinations


class Triangle:
    """A class for Triangles

    Contains defining properties of triangle and also methods for finding encompassing circle and data formatting.

    Parameters
    ----------
    vertices : List[Coordinates]
        A list of the triangles vertices
    min_diff : str
        An optional string of the minimum difficulty that should be found in the triangle (Defaults to '5.0')
    max_diff : str
        An optional string of the maximum difficulty that should be found in the triangle (Defaults to '5.15')
    """
    vertices = []
    vertices_array = None
    """A numpy array of the vertices in lon, lat order
    """
    minDiff = '5.0'
    maxDiff = '5.15'
    _centroid = None
    _circle_radius = None
    _mini_center = None
    _mini_radius = None

    def __init__(self, vertices: List[Coordinate], min_diff: str = '5.0', max_diff: str = '5.15'):
        self.vertices = vertices
        self.vertices_array = np.array([[a.lon, a.lat] for a in self.vertices])

        self.minDiff = min_diff
        self.maxDiff = max_diff

    def split_triangle(self) -> List['Triangle']:
        """Splits triangle into two triangles

        "Draws" a line from the center of the longest edge to the point not contained on the longest edge.

        Returns
        -------
        split_triangle : List[Triangle]
            A list containing the two new triangles

        """
        # find longest side
        max_length = 0
        max_side = None
        for side in combinations(self.vertices, 2):
            length = side[0] - side[1]
            if length > max_length:
                max_side = side
                max_length = length

        odd_point = [p for p in self.vertices if p not in max_side][0]

        # find midpoint of longest side
        midpoint = max_side[0] / max_side[1]

        # Create and return two new triangles
        return [Triangle([midpoint, odd_point, a]) for a in max_side]

    def split_difficulty(self) -> List['Triangle']:
        """Split the triangle by difficulty

        Splits From 5.0 to 5.15, does not attempt to split as few times as possible as with geographic splits.

        Returns
        -------
        split_triangle : List[Triangle]
            16 Triangles, one for each difficulty
        """
        difficulty = ['5.{}'.format(a) for a in range(16)]
        return [Triangle(self.vertices, d, d) for d in difficulty]

    @property
    def centroid(self) -> Coordinate:
        """Finds the centroid of the triangle

        Unfortunately not the center of the smallest circle that encloses all the vertices

        Returns
        -------
        centroid : Coordinate
            The triangle's Centroid
        """
        if self._centroid is None:
            cent_lat = sum([a.lat for a in self.vertices]) / 3
            cent_lon = sum([a.lon for a in self.vertices]) / 3

            self._centroid = Coordinate(cent_lat, cent_lon)

        return self._centroid

    @property
    def circle_radius(self) -> float:
        """The radius of the circle that encloses all points centered at the centroid

        Not necessarily the smallest radius possible to enclose all points

        Returns
        -------
        centroid_radius : float
            radius needed for circle centered at the centroid to enclose all points
        """
        if self._circle_radius is None:
            self._circle_radius = max([a - self.centroid for a in self.vertices])

        return self._circle_radius

    def find_miniball(self):
        """Finds the "miniball," the smallest circle that can enclose all of the triangles vertices

        Returns
        -------
        nothing, values are stored in "private" attributes
        """
        c, r2 = miniball.get_bounding_ball(self.vertices_array)

        self._mini_center = Coordinate(c[1], c[0])
        self._mini_radius = sqrt(r2)

    @property
    def mini_center(self) -> Coordinate:
        """Center of the miniball
            Value is cached once found

        Returns
        -------
        mini_center : Coordinate
            The center of the miniball

        """
        if self._mini_center is None:
            self.find_miniball()
        return self._mini_center

    @property
    def mini_radius(self) -> float:
        """Radius of the miniball
            Value is cached once found

        Returns
        -------
        mini_radius : float
            radius of the miniball

        """
        if self._mini_radius is None:
            self.find_miniball()
        return self._mini_radius

    @property
    def mini_edge(self) -> Coordinate:
        """The "Mini edge"

        Returns the coordinate of the eastern most point on the miniball.

        Returns
        -------
        mini_edge : Coordinate
        """
        return Coordinate(self.mini_center.lat,
                          self.mini_center.lon + self.mini_radius)

    @property
    def mini_miles(self) -> float:
        """The length of the mini-ball radius in miles

        Takes the curvature of the earth into account assuming the distance is east to west

        Returns
        -------
        mini_miles : float
            length of the radius in miles
        """
        c = self.mini_center.tuple
        e = self.mini_edge.tuple

        return distance(c, e).miles

    @property
    def plot_coordinates(self) -> np.array:
        """Coordinates that can be used in MATPLOTLIB to plot the closed triangle

        Deprecated by the use of modern geographic plotting libraries.

        Returns
        -------
        coordinates : np.array
            coordinates that can be sent to MATPLOTLIB to plot a closed triangle
        """
        cs = self.vertices_array
        # Add first element to end of array to close triangle
        cs = np.append(cs, [cs[0]], axis=0)

        # Transpose to group lat and lon
        cs = cs.transpose()

        return cs[0], cs[1]



