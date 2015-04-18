import numpy as np
import pandas as pd
import urllib2
import rdflib
import json
from fuzzywuzzy import fuzz


dataset_url = 'https://github.com/ailabitmo/ceur-ws-lod/releases/download/ceur-ws-crawler-v1.0.0/task-1-dataset.ttl'


def create_graph(data):
    """
    :type data: file
    :rtype: rdflib.Graph
    """
    g = rdflib.Graph()
    g.parse(data, format='n3')
    return g


def get_names_as_dict(g):
    """
    :type g: rdflib.Graph
    :rtype: dict
    """
    d = {}
    try:
        for i, row in enumerate(g.query('SELECT ?name ?person WHERE {?person a swrc:Person ; swrc:name ?name}')):
            name, person_uri = row
            if person_uri not in d:
                d[person_uri] = []
            d[person_uri].append(name)
    finally:
        with open('ceur-persons.json', 'w') as f:
            json.dump(d, f)
    return d


def compare_names(names1, names2):
    """
    :type p1: list of str
    :type p2: list of str
    :rtype: bool
    """
    for n1 in names1:
        for n2 in names2:
            if fuzz.WRatio(n1, n2) > 90:
                return True
    return False


def find_duplicates(persons):
    """
    :type persons: dict
    :rtype: list of list of str
    """
    duplicates = []
    try:
        while len(persons) > 0:
            dups = []
            uri, names = persons.popitem()
            try:
                print uri
                for u, n in persons.iteritems():
                    if compare_names(names, n):
                        dups.append(u)
            finally:
                if len(dups) > 0:
                    dups.append(uri)
                    duplicates.append(dups)
    finally:
        with open('ceur_duplicates.json', 'w') as f:
            json.dump(duplicates, f)


print 'Downloading data'
graph = create_graph(urllib2.urlopen(dataset_url))
print 'Transforming data'
data = get_names_as_dict(graph)
print 'Looking for duplicates'
find_duplicates(data)