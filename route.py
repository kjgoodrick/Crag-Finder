import re
from typing import List
from collections import defaultdict


class Route:
    """
    A class that stores data for a climbing route

    This class should be modified with extreme care to prevent errors when pulling from the cache. Most changes would
    be better placed in RatedRoute. This class contains all of the information returned from Mountain Project.
    """

    id = None
    name = None
    type = None
    rating = None
    stars = None
    starVotes = None
    pitches = None
    location = None
    url = None
    imgSqSmall = None
    imgSmall = None
    imgSmallMed = None
    imgMedium = None
    longitude = None
    latitude = None

    def __init__(self, data):
        self.__dict__ = data

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id


class RatedRoute(Route):
    """
    Class that includes additional rating attributes and methods
    """
    sport_type = 'Sport'
    rating_regex = r"5\.(\d+)([abcd+-]?)"

    def __init__(self, route):
        Route.__init__(self, route.__dict__)

    @property
    def kyle_score(self):
        if self.type == RatedRoute.sport_type and '5.5' <= self.rating <= '5.9':
            return 1 + self.stars
        else:
            return 0

    @property
    def num_rating(self):
        """A numeric representation of a climbs grade
        """
        return RatedRoute.str2num_rating(self.rating)

    @ staticmethod
    def str2num_rating(str_rating: str) -> float:
        """
        Converts a string rating to a numeric rating
        e.g. '5.9' -> 9, 5.10a -> 10.1, 5.11d -> 11.4
        modifiers are in this order:
        lower grade's d, -, base, a, b, +, c, d, higher grade's -

        Parameters
        ----------
        str_rating: str
            A string representing a climbing grade

        Returns
        -------
        float
            A numeric representation of the grade
        """
        # Find the grade and the modifier if one exists
        grade = re.match(RatedRoute.rating_regex, str_rating)
        base = int(grade.group(1))  # Climb's Grade
        suf = grade.group(2)  # Climb's Grade Modifier

        # map modifier
        # a, b, c, d, +, -> 1, 2, 3, 4, 2.5, -2.5
        dec = int(ord(suf) - 96) if len(suf) > 0 else 0
        dec = 2.5 if suf == '+' else dec
        dec = -2.5 if suf == '-' else dec

        return base + dec / 10

    @staticmethod
    def sort_crags(routes: List['RatedRoute'], parent_crag: str = None, base_only: bool = False):
        """
        Sorts crags by score, can filter out crags not within a given parent crag or that are not base level crags.

        Parameters
        ----------
        routes : List[RatedRoute]
            A list of RatedRoute objects
        parent_crag : str
            A string representing the parent crag, all returned crags will be a sub-crag of this crag
        base_only : bool
            Should be set to True if only base level crags should be returned, base level means a crag has no sub-crags

        Returns
        -------

        """
        if parent_crag is not None:
            child_routes = [r for r in routes if parent_crag in r.location]
        else:
            child_routes = routes

        if base_only:
            base_level_crags = [r.location[-1] for r in child_routes]
        else:
            base_level_crags = None

        child_crags = defaultdict(float)

        for r in child_routes:
            for l in r.location:
                child_crags[l] += r.kyle_score

        sorted_crags = sorted(child_crags.items(), key=lambda kv: kv[1], reverse=True)

        for c in sorted_crags:
            if not base_only or c[0] in base_level_crags:
                if c[1] > 0:
                    print("{}: {:5g}".format(c[0], c[1]))
