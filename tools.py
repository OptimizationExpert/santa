import math
from dataclasses import dataclass
from typing import List, Dict
@dataclass()
class Node():
    lat: float
    long: float
    pop: int
    name:str
    county:str
    id: int
    def __hash__(self):
        return hash(self.id)

import math

def latlon_to_xyz(node:Node, h=0):
    lat, lon = node.lat, node.long    # WGS84 constants
    a = 6378137.0          # semi-major axis (meters)
    e2 = 6.69437999014e-3  # eccentricity squared

    lat = math.radians(lat)
    lon = math.radians(lon)

    N = a / math.sqrt(1 - e2 * math.sin(lat)**2)

    x = (N + h) * math.cos(lat) * math.cos(lon)
    y = (N + h) * math.cos(lat) * math.sin(lon)
    z = (N * (1 - e2) + h) * math.sin(lat)

    return int(x), int(y), int(z)

def dist(node1:Node, node2:Node):
    lat1, lon1 = node1.lat, node1.long
    lat2, lon2 = node2.lat, node2.long

    # Earth radius in kilometers
    R = 6371.0

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return int(R * c)  # distance in km

Nodes = List[Node]
def create_nodes(df)-> Nodes:
    nodes = []
    for i in df.index:
        nodes.append(
            Node(
                lat=df.loc[i, 'lat'],
                long=df.loc[i, 'lng'],
                pop=df.loc[i, 'population'],
                name=df.loc[i, 'city'],
                county=df.loc[i, 'county'],
                id=i
            )
        )
    nodes.sort(key=lambda o: o.pop, reverse=False)
    return nodes
