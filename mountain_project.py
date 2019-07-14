from triangle import Triangle
from typing import List
from route import Route

from ipyleaflet import Map, Polygon
import random
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

cm = get_cmap(name='tab10')
cm255 = [[int(rgb * 255) for rgb in c] for c in cm.colors]
cmhex = ['#%02X%02X%02X' % tuple(c) for c in cm255]
colors = cycle(cmhex)


def rand_color():
    return next(colors)


def process_triangles(triangles: List[Triangle], m: Map = None):
    final_routes = set()
    final_triangles = set()
    for triangle in triangles:
        if triangle.mini_miles > 100:
            final_routes.update(process_triangles(triangle.split_triangle(), m))
        else:
            routes = get_routes(triangle, m)
            if len(routes) >= 500:
                if triangle.mini_miles > 2:
                    final_routes.update(process_triangles(triangle.split_triangle(), m))
                else:
                    final_routes.update(process_triangles(triangle.split_difficulty(), m))
            else:
                final_routes.update(routes)

    return final_routes


def get_routes(triangle: Triangle, m: Map = None) -> List[Route]:
    if m is None:
        print('Fetching results for triangle with radius {r:g} at ({lat:g}, {lon:g})'.format(r=triangle.mini_miles,
                                                                                             lat=triangle.mini_center.lat,
                                                                                             lon=triangle.mini_center.lon))
    else:
        color = rand_color()
        m_tri = Polygon(locations=[p.tuple for p in triangle.vertices], color=color, fill_color=color, fill_opacity=0.2)
        m.add_layer(m_tri)

    key = MP_API_KEY
    url = 'https://www.mountainproject.com/data/get-routes-for-lat-lon'
    params = {'lat': str(triangle.mini_center.lat),
              'lon': str(triangle.mini_center.lon),
              'maxDistance': str(triangle.mini_miles),
              'maxResults': str(500),
              'minDiff': triangle.minDiff,
              'maxDiff': triangle.maxDiff,
              'key': key}
    r = send_request(url, params)
    r = r.json()

    return [Route(b) for b in r['routes']]


def validate_key():
    global MP_API_KEY

    if MP_API_KEY is not None and MP_API_KEY != 'your_key_here':
        return

    print('Please obtain a Mountain Project API key before continuing.')
    print('API keys can be obtained from: mountainproject.com/data')
    MP_API_KEY = input('Please enter API key here: ')

    gen_settings.gen_settings(MP_API_KEY)

    return
