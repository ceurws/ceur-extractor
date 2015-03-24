#! /usr/bin/env python
# -*- coding: utf-8 -*-


class PDFParserLibMock():
    def __init__(self, file_path):
        print "Init file path"

    def getPaperTitle(self):
        return "Paper title"

    def getAuthors(self):
        authors = []
        authors.append({"full_name":"Full name 1", "organization": { "title":"Org title 1", "country":"Country 1"}})
        authors.append({"full_name":"Full name 2", "organization": { "title":"Org title 2"}})
        authors.append({"full_name":"Full name 3"})
        return authors
    
    def getCitedWorks(self):
        works = []
        works.append({"title":"Work title 1","doi":"32323","year":2015,"journal":"Journal title 1"})
        works.append({"title":"Work title 2","doi":"32-23323"})
        works.append({"title":"Work title 3","year":2015,"journal":"Journal title 3"})
        works.append({"title":"Work title 4","journal":"Journal title 4"})
        return works

    def getGrants(self):
        grants = []
        grants.append({"id":"3232","title":"Grant title 1"})
        grants.append({"id":"31-32","title":"Grant title 2"})
        grants.append({"title":"Grant titlee 3"})
        return grants

    def getFundingAgencies(self):
        return ["FA1", "FA2", "FA3"]

    def getEUProjects(self):
        return ["EU1", "EU2", "EU3"]

    def getNewOntologies(self):
        return ["BIBO", "FOAF", "DB"]

    def getRelatedOntologies(self):
        return ["SWC", "AISSO", "FOAF"]

