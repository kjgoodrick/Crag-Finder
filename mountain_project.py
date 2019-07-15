"""Mountain Project

This module contains methods and attributes for interfacing with Mountain Project

Notes
-----
In order to prevent the cache from being cleared, modification of the send_request method should be avoided.
"""
from triangle import Triangle
from typing import List
from route import Route

from ipyleaflet import Map, Polygon
from matplotlib.cm import get_cmap
from itertools import cycle

import requests
import gen_settings
from joblib import Memory

cache_dir = 'cache'
memory = Memory(cache_dir, verbose=0)


@memory.cache
def send_request(url, params):
    return requests.get(url, params=params)


MP_API_KEY = None
"""Stores the MP API Key
"""

# Create a color map generator
cm = get_cmap(name='tab10')
cm255 = [[int(rgb * 255) for rgb in c] for c in cm.colors]
cm_hex = ['#%02X%02X%02X' % tuple(c) for c in cm255]
colors = cycle(cm_hex)


def next_color():
    """
    Returns the next color in the color map generator
    Returns
    -------
    color : str
        A string containing the next hex color code, cycles forever through cm_hex
    """
    return next(colors)


def process_triangles(triangles: List[Triangle], m: Map = None):
    """
    Searches through a list of triangles and finds the routes within each triangle, optionally plots the results on a
    map as it goes. If a triangle is too large or contains to many routes it is split into smaller triangles and the
    method is recursively called with the split triangles as an argument. Splitting can also be done by grade if the
    triangles get too small, but still contain too many routes. Routes and the final set of triangles are stored in
    a set.
    Parameters
    ----------
    triangles : List[Triangle]
        A list of triangles to find routes in
    m : Map
        An optional map object that can be used to plot the progress as it goes. If no map is provided progress is
        reported in the log.

    Returns
    -------
    final_routes: set
        A set of routes within the triangles

    """
    # Create Storage sets
    final_routes = set()
    final_triangles = set()

    for triangle in triangles:
        # If the triangle is too large break into two smaller triangles and try again
        if triangle.mini_miles > 100:  # Triangle is too large
            final_routes.update(process_triangles(triangle.split_triangle(), m))
        else:  # Triangle is not too large
            # find routes within the triangle
            routes = get_routes(triangle, m)

            # Check if there are more routes in triangle than MP can return in one call
            if len(routes) >= 500:  # Too many routes within triangle
                # Check if triangle is smaller than average crag size
                if triangle.mini_miles > 2:  # Triangle is not too small
                    # Try again with even smaller triangles
                    final_routes.update(process_triangles(triangle.split_triangle(), m))
                else:  # Triangle is smaller than average crag
                    # Split the triangle by difficulty and try again
                    # At this point if there are more than 500 routes of a grade within 2 miles some will be lost
                    # This is highly unlikely though, so I do not think it will ever need further subdivision.
                    final_routes.update(process_triangles(triangle.split_difficulty(), m))
            else:  # Not too many triangles in the triangle
                # Add routes in the triangle to the set
                final_routes.update(routes)

    # Send newly found routes back to the previous levels
    return final_routes


def get_routes(triangle: Triangle, m: Map = None) -> List[Route]:
    """
    Find routes within a triangle (sort of) and plot on an optional map
    MP allows queries from a central point with a radius, so a circle is formed that encompasses all off the triangle's
    vertices; however, the circle will also contain some area that is not in the triangle.

    Parameters
    ----------
    triangle : Triangle
        Triangle to search in
    m : Map
        Optional Map object to plot triangles on. If no map is given progress is reported in the log.

    Returns
    -------
    routes : List[Route]
        a list of routes within the triangle, plus some nearby potentially.

    """
    if m is None:  # No map, print progress in log
        print('Fetching results for triangle with radius {r:g} at ({lat:g}, {lon:g})'.format(r=triangle.mini_miles,
                                                                                             lat=triangle.mini_center.lat,
                                                                                             lon=triangle.mini_center.lon))
    else:  # Map, plot progress in map
        color = next_color()
        m_tri = Polygon(locations=[p.tuple for p in triangle.vertices], color=color, fill_color=color, fill_opacity=0.2)
        m.add_layer(m_tri)

    # Form Query
    key = MP_API_KEY
    url = 'https://www.mountainproject.com/data/get-routes-for-lat-lon'
    params = {'lat': str(triangle.mini_center.lat),
              'lon': str(triangle.mini_center.lon),
              'maxDistance': str(triangle.mini_miles),
              'maxResults': str(500),  # 500 is maximum for MP
              'minDiff': triangle.minDiff,
              'maxDiff': triangle.maxDiff,
              'key': key}

    # Send request and parse data
    r = send_request(url, params)
    r = r.json()

    return [Route(b) for b in r['routes']]


def validate_key():
    """
    Checks to see if a MP key has been provided. If not prompts for one and updates the settings for future use.

    Returns
    -------
        nothing
    """
    # A global variable, the horror!
    global MP_API_KEY

    # If we wave a key and it's not the default filler, continue
    if MP_API_KEY is not None and MP_API_KEY != 'your_key_here':
        return

    # No API key has been provided so prompt for one
    print('Please obtain a Mountain Project API key before continuing.')
    print('API keys can be obtained from: mountainproject.com/data')
    MP_API_KEY = input('Please enter API key here: ')

    # Update settings with new found API key
    gen_settings.gen_settings(MP_API_KEY)
