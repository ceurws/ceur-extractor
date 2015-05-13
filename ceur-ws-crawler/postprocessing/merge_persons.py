import urllib2
import rdflib
from rdflib import URIRef
from rdflib.namespace import OWL
from itertools import permutations
import json
from fuzzywuzzy import fuzz
from sys import argv


def create_graph(data):
    """
    :type data: file
    :rtype: rdflib.Graph
    """
    g = rdflib.Graph()
    g.parse(data, format='turtle')
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
    count = 0
    duplicates = []
    try:
        while len(persons) > 0:
            dups = []
            uri, names = persons.popitem()
            try:
                count += 1
                print count, uri
                for u, n in persons.iteritems():
                    if compare_names(names, n):
                        dups.append(u)
            finally:
                if len(dups) > 0:
                    dups.append(uri)
                    duplicates.append(dups)
    finally:
        with open('merged_persons.json', 'w') as f:
            json.dump(duplicates, f, indent=4, separators=(',', ': '))
        return duplicates


def create_sameas(duplicates):
    """
    :type duplicates: list of list of str
    :rtype: rdflib.Graph
    """
    g = rdflib.Graph()
    for group in duplicates:
        perm = permutations(group, 2)
        for p in perm:
            g.add((URIRef(p[0]), OWL.sameAs, URIRef(p[1])))
    return g


with open(argv[1], 'r') as f:
    print 'Loading data form file: ' + argv[1]
    graph = create_graph(f)
print 'Transforming data'
data = get_names_as_dict(graph)
print 'Looking for duplicates'
duplicates = find_duplicates(data)
print 'Saving duplicates as OWL:sameAs'
persons_sameas = create_sameas(duplicates)
with open('persons_sameas.ttl', 'w') as f:
    f.write(persons_sameas.serialize(format='turtle'))

