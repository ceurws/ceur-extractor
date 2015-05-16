from rdflib import Graph
from sys import argv


if len(argv) != 3:
    print 'Usage: python merge_ttls.py <file_1> <file_2>'
    exit()

g1 = Graph()
g2 = Graph()

with open(argv[1], 'r') as f:
    g1.parse(f, format='turtle')
with open(argv[2], 'r') as f:
    g2.parse(f, format='turtle')

with open('sempub2015-task1.ttl', 'w') as f:
    f.write((g1 + g2).serialize(format='turtle'))