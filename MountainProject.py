from Triangle import Triangle
from typing import List
from Route import Route

import requests
from joblib import Memory
cache_dir = 'cache'
memory = Memory(cache_dir, verbose=0)


MP_API_KEY = None


@memory.cache
def send_request(url, params):
    return requests.get(url, params=params)


def process_triangles(triangles: List[Triangle]):
    final_routes = set()
    final_triangles = set()
    for triangle in triangles:
        if triangle.mini_miles > 100:
            final_routes.update(process_triangles(triangle.split_triangle()))
        else:
            routes = get_routes(triangle)
            if len(routes) >= 500:
                if triangle.mini_miles > 2:
                    final_routes.update(process_triangles(triangle.split_triangle()))
                else:
                    final_routes.update(process_triangles(triangle.split_difficulty()))
            else:
                final_routes.update(routes)

    return final_routes


def get_routes(triangle: Triangle) -> List[Route]:
    print('Fetching results for triangle with radius {r:g} at ({lat:g}, {lon:g})'.format(r=triangle.mini_miles,
                                                                                         lat=triangle.mini_center.lat,
                                                                                         lon=triangle.mini_center.lon))
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


