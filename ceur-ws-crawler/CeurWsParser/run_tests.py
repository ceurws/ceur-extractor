#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import traceback
import argparse
from csv import Dialect

from rdflib import Graph, Literal, URIRef, util
from rdflib.plugins.stores import sparqlstore
from rdflib.namespace import FOAF, DCTERMS, DC, XSD

import config
from namespaces import SWRC, BIBO, TIMELINE, SWC, SKOS


QUERY_FILENAME = 'query.sparql'
EXPECTED_FILENAME = 'expected.output'
TESTS_ROOT_DIR = 'tests'


def topython(graph, term):
    if isinstance(term, Literal):
        if term.datatype.eq(URIRef("http://www.w3.org/2001/XMLSchema#string")):
            return u'"%s"' % term.value
        elif term.datatype.eq(URIRef("http://www.w3.org/2001/XMLSchema#boolean")):
            return u'"true"' if term.value else u'"false"'
    return term.n3(graph.namespace_manager)


def from_n3(string):
    term = util.from_n3(string)
    if isinstance(term, Literal):
        if term.datatype is None and term.language is None:
            term = Literal(term, datatype=URIRef('xsd:string'))
    return term


def normalize(namespace_manager, term):
    if isinstance(term, Literal) and term.datatype is not None:
        return Literal(term, datatype=namespace_manager.normalizeUri(term.datatype))
    return term


def read_csv(utf8_data, dialect=Dialect.delimiter):
    csv_reader = csv.reader(utf8_data, dialect=dialect, quoting=csv.QUOTE_NONE)
    lines = []
    for row in csv_reader:
        lines.append([from_n3(unicode(cell, 'utf-8')) for cell in row])
    return lines


def print_list(l):
    for row in l:
        if isinstance(row, list):
            print ', '.join(map(repr, row))
        else:
            print row


def main(args):
    number_of_passed = 0
    number_of_failed = 0
    number_of_failed_with_exception = 0

    graph = Graph(
        sparqlstore.SPARQLStore(config.sparqlstore['test_url'],
                                context_aware=False))
    graph.bind('foaf', FOAF)
    graph.bind('xsd', XSD)
    graph.bind('swrc', SWRC)
    graph.bind('swc', SWC)
    graph.bind('skos', SKOS)
    graph.bind('bibo', BIBO)
    graph.bind('dcterms', DCTERMS)
    graph.bind('dc', DC)
    graph.bind('timeline', TIMELINE)

    for f in os.listdir(args.testdir):
        if ('test' in args and f == args.test) or not 'test' in args:
            print "========================="
            print "[TEST %s] Running..." % f
            try:
                passed = True
                with open('%s/%s/%s' % (args.testdir, f, QUERY_FILENAME)) as query_file:
                    result = graph.query(query_file.read())

                    results = []
                    for r in result:
                        result_line = [normalize(graph.namespace_manager, x) for x in r]
                        results.append(result_line)

                    print "[TEST %s] Number of results: %s" % (f, len(results))

                    with open('%s/%s/%s' % (args.testdir, f, EXPECTED_FILENAME), 'rb') as expected_file:
                        expected = read_csv(expected_file)
                        print "[TEST %s] Number of expected results: %s" % (f, len(expected))
                        if len(results) != len(expected):
                            passed = False
                        else:
                            for row in expected:
                                if row not in results:
                                    print "[TEST %s] [%s] not found!" % (f, ', '.join(map(repr, row)))
                                    print "[TEST %s] Query results:" % f
                                    print_list(results)
                                    passed = False
                                    break

                    if passed:
                        print "[TEST %s] Passed!" % f
                        number_of_passed += 1
                    else:
                        print "[TEST %s] Failed!" % f
                        number_of_failed += 1

            except:
                print "[TEST %s] Failed with exception!" % f
                number_of_failed_with_exception += 1
                traceback.print_exc()

    print "\n======RESULTS======\n"
    print "Passed: %s" % number_of_passed
    print "Failed: %s" % number_of_failed
    print "Failed with exception: %s" % number_of_failed_with_exception


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Run the test SPARQL queries for Task 1')
    parser.add_argument('--test', required=False)
    parser.add_argument('--testdir', required=False, default=TESTS_ROOT_DIR)
    args = parser.parse_args()
    main(args)
