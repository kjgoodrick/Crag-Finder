import mountain_project
from coordinate import Coordinate
from triangle import Triangle
from route import RatedRoute

import configparser
import gen_settings

# Setup configuration
config = configparser.ConfigParser()
config.read(gen_settings.SETTINGS_FILE)

# Try to read MP API Key, we will prompt for one later so no need to do anything on error
try:
    mountain_project.MP_API_KEY = config['MP API']['key']
except KeyError:
    pass

# Check if we have a valid key
mountain_project.validate_key()

# Define the corners of CO
sw_co = Coordinate(36.680672, -109.354249)
ne_co = Coordinate(41.051978, -101.913311)

# Calculate the other corners of CO
se_co = Coordinate(sw_co.lat, ne_co.lon)
nw_co = Coordinate(ne_co.lat, sw_co.lon)

# Form triangles from boundary of CO
t1 = Triangle([sw_co, se_co, nw_co])
t2 = Triangle([nw_co, ne_co, se_co])

# Find all routes in CO
routes = mountain_project.process_triangles([t1, t2])

# Convert to RatedRoute
routes = [RatedRoute(r) for r in routes]

# Find all the Crags in Boulder and sort by rating
RatedRoute.sort_crags(routes, 'Boulder')
