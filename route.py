"""Route classes
"""
import re
from typing import List, Set
from collections import defaultdict
from enum import Enum

from class_property import classproperty, ClassPropertyMetaClass
import configparser


class RouteType(Enum):
    """Enum for types of climbs

    This list was generated from climbs in Colorado others may exist
    """
    aid = 'aid'
    alpine = 'alpine'
    boulder = 'boulder'
    ice = 'ice'
    mixed = 'mixed'
    snow = 'snow'
    sport = 'sport'
    tr = 'tr'
    trad = 'trad'


class Route:
    """
    A class that stores data for a climbing route

    This class should be modified with extreme care to prevent errors when pulling from the cache. Most changes would
    be better placed in RatedRoute. This class contains all of the information returned from Mountain Project.
    """

    id: int = None
    name: str = None
    type: str = None
    rating: str = None
    stars: float = None
    starVotes: int = None
    pitches: int = None
    location: List[str] = None
    url: str = None
    imgSqSmall: str = None
    imgSmall: str = None
    imgSmallMed: str = None
    imgMedium: str = None
    longitude: float = None
    latitude: float = None

    def __init__(self, data):
        """
        Creates a new route object from a dictionary of attributes

        Parameters
        ----------
        data: dict
            A dictionary of attributes
        """
        self.__dict__ = data

    def __hash__(self):
        """
        Hash and eq allow the objects to be cached

        Returns
        -------
        hash: str
            Hash includes only the id
        """
        return hash(self.id)

    def __eq__(self, other):
        """
        For caching

        Parameters
        ----------
        other: Route
            The route to be compared
        Returns
        -------
        eq: bool
            Checks equality and returns a bool or NotImplemented if other is not the same type
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id


class RatedRoute(Route, metaclass=ClassPropertyMetaClass):
    """
    Class that includes additional rating attributes and methods

    This objects of this class are created after pulling from the cache so this class can be modified without affecting
    the cache.
    """
    min_rating = '5.0'
    """The minimum rating a route should have to be included in the score
    """
    max_rating = '5.15'
    """The maximum rating a route should have to be included in the score
    """
    min_pitches = 0
    """The minimum number of pitches a route should have to be included in the score
    """
    max_pitches = 1
    """The maximum number of pitches a route should have to be included in the score
    """

    required_types: Set[RouteType] = set()
    """The climbing types that must be part of a route to be included in the score
    """
    optional_types: Set[RouteType] = set()
    """The climbing types that are desired but not required to be part of the score
    """
    prohibited_types: Set[RouteType] = set()
    """The climbing types that may not be part of a route if it is included in the score
    """

    rating_regex = r"5\.(\d+)([abcd+-]?)"
    """Regex used to parse the climb's rating
    
    Currently does not support changing score based on exposure, but it does not break the parsing if they are included
    """

    def __init__(self, route):
        """
        Creates a rated route from a normal route

        Parameters
        ----------
        route: Route
            The route to be rated
        """
        Route.__init__(self, route.__dict__)
        # Parse the route types
        self.types: Set[RouteType] = type(self).cs_types2enum(self.type)

    @classproperty
    def min_num_rating(cls) -> float:
        """The minimum rating in numerical form

        See :meth:`route:RatedRoute:str2num_rating` for more details
        """
        return cls.str2num_rating(cls.min_rating)

    @classproperty
    def max_num_rating(cls) -> float:
        """The maximum rating in numerical form

        See :meth:`route:RatedRoute:str2num_rating` for more details
        """
        return cls.str2num_rating(cls.max_rating)

    @property
    def desired_type(self) -> bool:
        """Checks if the route is a desired type

        Uses the class's required, optional, and prohibited properties

        Returns
        -------
        desired: bool
            Whether the route is a desirable type or not
        """
        cls = type(self)
        # Check if all required types are present
        required = cls.required_types <= self.types
        # Make sure something desired is present
        desired = (cls.optional_types | cls.required_types) & self.types
        # Check if prohibited types are present
        prohibited = cls.prohibited_types & self.types

        return required and desired and not prohibited

    @property
    def score(self) -> float:
        """The route's score

        Calculates the route's score and returns it. If the route is undesirable the score is 0 otherwise it is:

        ..math::
        score = 1 + \\sqrt{stars}

        Returns
        -------
        score: float
            The route's score
        """
        if self.desired_type and type(self).min_num_rating <= self.num_rating <= type(self).max_num_rating:
            return 1 + self.stars ** 0.5
        else:
            return 0

    @property
    def num_rating(self):
        """A numeric representation of a climbs grade

        See :meth:route:RatedRoute:`str2num_rating` for more details

        Returns
        -------
        rating: float
            The route's rating in a numeric form
        """
        return RatedRoute.str2num_rating(self.rating)

    @staticmethod
    def cs_types2enum(cs_types: str) -> Set[RouteType]:
        """Parses a comma separated string of types

        Parameters
        ----------
        cs_types: str
            A comma separated string of types

        Returns
        -------
        types: Set[RouteType]
            A list of types
        """
        return set([RouteType[t.strip().lower()] for t in cs_types.split(',') if t != ""])

    @staticmethod
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
        # If there is a parent crag find the routes within that crag
        if parent_crag is not None:
            child_routes = [r for r in routes if parent_crag in r.location]
        else:
            child_routes = routes

        # If only base level crags should be returned find them
        if base_only:
            base_level_crags = [r.location[-1] for r in child_routes]
        else:
            base_level_crags = None

        # Storage for the crags to be returned
        child_crags = defaultdict(float)

        # Loop through the routes and add each score to all of the routes crags
        for r in child_routes:
            for l in r.location:
                child_crags[l] += r.score

        # Sort the dictionary by score
        sorted_crags = sorted(child_crags.items(), key=lambda kv: kv[1], reverse=True)

        # Print the results omitting non-base-level crags if requested and those with a score of 0.
        for c in sorted_crags:
            if not base_only or c[0] in base_level_crags:
                if c[1] > 0:
                    print("{}: {:5g}".format(c[0], c[1]))

    @classmethod
    def parse_config(cls, config: configparser.ConfigParser):
        """Parse the config file for route specific settings

        Parameters
        ----------
        config: configparser.ConfigParser
            A configparser with settings for the route scoring

        Returns
        -------
        nothing
        """
        score_conf = config['SCORE']

        # Load route score settings
        RatedRoute.required_types = RatedRoute.cs_types2enum(score_conf['required'])
        RatedRoute.optional_types = RatedRoute.cs_types2enum(score_conf['optional'])
        prohibited = score_conf['prohibited']
        # If prohibited is other all are prohibited except for those in required and optional
        if prohibited.lower() == 'other':
            prohibited = {t for t in RouteType} - (RatedRoute.required_types | RatedRoute.optional_types)
            RatedRoute.prohibited_types = prohibited
        else:
            RatedRoute.prohibited_types = RatedRoute.cs_types2enum(prohibited)
        RatedRoute.min_rating = score_conf['min_rating']
        RatedRoute.max_rating = score_conf['max_rating']
        RatedRoute.min_pitches = int(score_conf['min_pitches'])
        RatedRoute.max_pitches = int(score_conf['max_pitches'])
