from typing import List
from coordinate import Coordinate
from math import sqrt
import numpy as np
import miniball
from geopy.distance import distance
from itertools import combinations


class Triangle:
    """A class for Triangles"""
    vertices = []
    vertices_array = None
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

    def split_triangle(self):
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

        return [Triangle([midpoint, odd_point, a]) for a in max_side]

    def split_difficulty(self):
        difficulty = ['5.{}'.format(a) for a in range(16)]
        return [Triangle(self.vertices, d, d) for d in difficulty]

    @property
    def centroid(self):
        if self._centroid is None:
            cent_lat = sum([a.lat for a in self.vertices]) / 3
            cent_lon = sum([a.lon for a in self.vertices]) / 3

            self._centroid = Coordinate(cent_lat, cent_lon)

        return self._centroid

    @property
    def circle_radius(self):
        if self._circle_radius is None:
            self._circle_radius = max([a - self.centroid for a in self.vertices])

        return self._circle_radius

    def find_miniball(self):
        c, r2 = miniball.get_bounding_ball(self.vertices_array)

        self._mini_center = Coordinate(c[1], c[0])
        self._mini_radius = sqrt(r2)

    @property
    def mini_center(self):
        if self._mini_center is None:
            self.find_miniball()
        return self._mini_center

    @property
    def mini_radius(self):
        if self._mini_radius is None:
            self.find_miniball()
        return self._mini_radius

    @property
    def mini_edge(self):
        return Coordinate(self.mini_center.lat,
                          self.mini_center.lon + self.mini_radius)

    @property
    def mini_miles(self):
        c = self.mini_center.tuple
        e = self.mini_edge.tuple

        return distance(c, e).miles

    @property
    def plot_coordinates(self):
        cs = self.vertices_array
        cs = np.append(cs, [cs[0]], axis=0)

        cs = cs.transpose()

        return cs[0], cs[1]



