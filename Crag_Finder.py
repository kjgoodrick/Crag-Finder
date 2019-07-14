import mountain_project
from coordinate import Coordinate
from triangle import Triangle
from route import RatedRoute

import configparser
import gen_settings

config = configparser.ConfigParser()
config.read(gen_settings.SETTINGS_FILE)

try:
    mountain_project.MP_API_KEY = config['MP API']['key']
except KeyError:
    pass

mountain_project.validate_key()

sw_co = Coordinate(36.680672, -109.354249)
ne_co = Coordinate(41.051978, -101.913311)

se_co = Coordinate(sw_co.lat, ne_co.lon)
nw_co = Coordinate(ne_co.lat, sw_co.lon)

t1 = Triangle([sw_co, se_co, nw_co])
t2 = Triangle([nw_co, ne_co, se_co])

routes = mountain_project.process_triangles([t1, t2])

routes = [RatedRoute(r) for r in routes]

RatedRoute.sort_crags(routes, 'Boulder')
