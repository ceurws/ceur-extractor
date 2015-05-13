#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alexander'
import os, re, codecs

import PdfExtractionLib as pdf
import metadata_information
def main_test():
    f_name = os.path.join(os.path.dirname(__file__), "pdfs", "Vol-315-paper1.pdf")

    pdf_parser = PDFmetadataExtractionLib(f_name, pdf.get_html_and_txt)

class PDFmetadataExtractionLib():
    def __init__(self, file_path, pdf_converter_func):
        try:
            if not os.path.isfile(file_path):
                print(u"There is no file: {0}".format(file_path))
                return
            self.filename = file_path
            self.pdf_information = {}
            dict_data = pdf_converter_func(self.filename)

            self.pdf_information = metadata_information.get_information(dict_data)
            a = 1
        except Exception as err:
            print("PDFmetadataExtractionLib __init__ -> {0}".format(err))
    def getPaperTitle(self):
        return self.pdf_information.get("title")
    def getAuthors(self):
        authors = []
        # authors.append({"full_name":"Full name 1", "organization": { "title":"Org title 1", "country":"Country 1"}})
        # authors.append({"full_name":"Full name 2", "organization": { "title":"Org title 2"}})
        # authors.append({"full_name":"Full name 3"})
        if "authors" in self.pdf_information:
            return self.pdf_information["authors"]
        return authors

    def getCitedWorks(self):
        works = []
        # works.append({"title":"Work title 1","doi":"32323","year":2015,"journal":"Journal title 1"})
        # works.append({"title":"Work title 2","doi":"32-23323"})
        # works.append({"title":"Work title 3","year":2015,"journal":"Journal title 3"})
        # works.append({"title":"Work title 4","journal":"Journal title 4"})
        if 'cited_works' in self.pdf_information:
            return self.pdf_information["cited_works"]
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
if __name__ == "__main__":
    main_test()