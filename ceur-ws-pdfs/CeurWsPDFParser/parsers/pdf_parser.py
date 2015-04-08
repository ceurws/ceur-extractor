#! /usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import os
import tempfile
import re
from cStringIO import StringIO
import urllib
from urllib2 import HTTPError

import rdflib
from rdflib import URIRef, Graph, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLStore

import config
from base import Parser, find_university_in_dbpedia, create_proceedings_uri, create_publication_uri, clean_string
from pdf_parser_lib_mock import PDFParserLibMock
from namespaces import SWRC, DBPEDIAOWL, BIBO 
from rdflib.namespace import RDF, RDFS, FOAF, DCTERMS, DC, XSD

import pdf_extraction_lib as pdf_convert
from metadata_extraction_lib import PDFmetadataExtractionLib


class PDFParser(Parser):
    def __init__(self, grab, task, graph, spider=None):
        Parser.__init__(self, grab, task, graph, spider=spider)
        #DBPedia SPARQL Endpoint
        self.dbpedia = Graph(SPARQLStore(config.sparqlstore['dbpedia_url'],
                                         context_aware=False), namespace_manager=self.graph.namespace_manager)

    def write(self):
        print "[TASK %s][PDFParser] Count of authors: %s. Count of cited works %s" % (
            self.task.url, len(self.data['authors']), len(self.data['cited_works']))
        triples = []

        proceedings = URIRef(self.data['workshop'])
        resource = create_publication_uri(self.data['workshop'], self.data['file_name'])
        
        triples.append((proceedings, DCTERMS.hasPart, resource))
        triples.append((resource, RDF.type, FOAF.Document))
        triples.append((resource, DCTERMS.partOf, proceedings))
        triples.append((resource, RDF.type, SWRC.InProceedings))
        triples.append((resource, DC.title, Literal(self.data['title'], datatype=XSD.string)))


        for author in self.data['authors']:
                agent = URIRef(config.id['person'] + urllib.quote(author["full_name"].encode('utf-8')))
                triples.append((agent, RDF.type, FOAF.Agent))
                triples.append((agent, FOAF.name, Literal(author["full_name"], datatype=XSD.string)))
                triples.append((resource, DC.creator, agent))
                triples.append((resource, FOAF.maker, agent))
                triples.append((agent, FOAF.made, resource))
                
                if "organization" in author:
                    organization = URIRef(config.id['affiliation'] + urllib.quote(author["organization"]["title"].encode('utf-8')))
                    triples.append((agent, SWRC.affiliation, organization))
                    triples.append((organization, RDF.type, FOAF.Organization))
                    triples.append((organization, BIBO.name, Literal(author["organization"]["title"], datatype=XSD.string)))

                    # organization country
                    if "country" in author["organization"]:
                        country = URIRef(config.id['country'] + urllib.quote(author["organization"]["country"].encode('utf-8')))
                        triples.append((organization, DBPEDIAOWL.country, country))
                        triples.append((country, FOAF.name, Literal(author["organization"]["country"], datatype=XSD.string)))
                        triples.append((country, RDF.type, DBPEDIAOWL.Country))
 
                # cited works
        for cited_work in self.data['cited_works']:
                cw = URIRef(config.id['cited_work'] + urllib.quote(cited_work["title"].encode('utf-8')))
                triples.append((cw, RDF.type, BIBO.Document))
                triples.append((cw, BIBO.title, Literal(cited_work["title"], datatype=XSD.string)))
                if "doi" in cited_work:
                    triples.append((cw, BIBO.doi, Literal(cited_work["doi"], datatype=XSD.string)))
                if "year" in cited_work:
                    triples.append((cw, BIBO.created, Literal(cited_work["year"], datatype=XSD.string)))
                if "journal" in cited_work:
                    journal = URIRef(config.id['journal'] + urllib.quote(cited_work["journal"].encode('utf-8')))
                    triples.append((cw, BIBO.isPartOf, journal))
                    triples.append((journal, RDF.type, BIBO.Journal))
                    triples.append((journal, BIBO.title, Literal(cited_work["journal"], datatype=XSD.string)))
            
                    
        # grants and projects
        # ontologies
        self.write_triples(triples)

    def parse_template_1(self):
        
        self.data['workshop'] = self.task.url.rsplit('/',1)[0]+"/"

        self.data['file_name'] = self.task.url.rsplit('/')[-1]
        self.data['id'] = self.data['file_name'].rsplit('.', 1)[:-1][0]
        self.data['file_location'] = "%s/%s" % (tempfile.gettempdir(), self.data['file_name'])

        try:
            try:
                self.grab.response.save(self.data['file_location'])

                parser_lib = PDFmetadataExtractionLib(self.data['file_location'],pdf_convert.get_html_and_txt)
                self.data['title'] = parser_lib.getPaperTitle()
                self.data['authors'] = parser_lib.getAuthors()
                self.data['cited_works'] = parser_lib.getCitedWorks()
                self.data['grants'] = parser_lib.getGrants()
                self.data['fundings'] = parser_lib.getFundingAgencies()
                self.data['eu_projects'] = parser_lib.getEUProjects()
                self.data['new_ontologies'] = parser_lib.getNewOntologies()
                self.data['related_ontologies'] = parser_lib.getRelatedOntologies()
                
            except:
                print "[TASK %s][PDFParser] Error parse%s" % (self.task.url, self.data['file_name'])
                traceback.print_exc()
                return None
            finally:
                os.remove(self.data['file_location'])
        except:
            pass


if __name__ == '__main__':
    print "not runnable"
