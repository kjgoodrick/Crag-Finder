import re
from typing import List
from collections import defaultdict


class Route:

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
    sport_type = 'Sport'
    rating_regex = r"5\.(\d+)([abcd]?)"

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
        grade = re.match(self.rating_regex, self.rating)
        base = int(grade.group(1))
        dec = grade.group(2)
        dec = int(ord(dec) - 96) if len(dec) > 0 else 0

        return base + dec / 10

    @staticmethod
    def sort_crags(routes: List['RatedRoute'], parent_crag: str = None, base_only: bool = False):
        """
        sort_crags
        :param routes:
        :param parent_crag:
        :param base_only:
        :return:
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
