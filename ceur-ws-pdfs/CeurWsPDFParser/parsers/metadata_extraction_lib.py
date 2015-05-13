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
        # grants.append({"id":"3232","title":"Grant title 1"})
        # grants.append({"id":"31-32","title":"Grant title 2"})
        # grants.append({"title":"Grant titlee 3"})
        if "grants" in self.pdf_information:
            return self.pdf_information["grants"]
        return grants

    def getFundingAgencies(self):
        if "funding_agencies" in self.pdf_information:
            return self.pdf_information["funding_agencies"]
        return []
        #return ["FA1", "FA2", "FA3"]

    def getEUProjects(self):
        if "EU_projects" in self.pdf_information:
            return self.pdf_information["EU_projects"]
        return []
        #return ["EU1", "EU2", "EU3"]

    def getNewOntologies(self):
        if "new_ontologies" in self.pdf_information:
            return self.pdf_information["new_ontologies"]
        return []
        #return ["BIBO", "FOAF", "DB"]

        # "related_ontologies": []
    def getRelatedOntologies(self):
        if "related_ontologies" in self.pdf_information:
            return self.pdf_information["related_ontologies"]
        return []
        #return ["SWC", "AISSO", "FOAF"]
    def get_header_part(self):
        if "header_part" in self.pdf_information:
            return self.pdf_information["header_part"]
        return ""
    def get_abstract_part(self):
        if "abstract_part" in self.pdf_information:
            return self.pdf_information["abstract_part"]
        return ""
    def get_acknowledgement_part(self):
        if "acknowledgement" in self.pdf_information:
            return self.pdf_information["acknowledgement"]
        return ""
    def get_biblioraphy_part(self):
        if "bibliography" in self.pdf_information:
            return self.pdf_information["bibliography"]
        return ""
    def make_damp(self):
        try:
            wh = None
            out_name = os.path.join(os.path.dirname(self.filename), os.path.basename(self.filename).replace(".pdf", ".damp_pdf"))

            wh = codecs.open(out_name, 'w', encoding="UTF-8")
            wh.write("Header_part\n")
            wh.write(u"{0}".format(self.get_header_part()))
            wh.write("\n***")
            wh.write("Title\n")
            wh.write(u"{0}".format(self.getPaperTitle()))
            wh.write("\n***")
            wh.write("Authors and affilations\n")
            for cur_author in self.getAuthors():
                wh.write("author -> '{0}'\n".format(cur_author.get("full_name", "")))
                wh.write("organisation -> '{0}'\n".format(cur_author.get("organisation", "")))
                #{"full_name":"Full name 1", "organization": { "title":"Org title 1", "country":"Country 1"}})
            wh.write("\n***")
            wh.write("Funding agencies\n")
            wh.write(u"{0}".format(self.getFundingAgencies()))
            wh.write(self.getPaperTitle())
        except Exception as err:
            print("make_damp")
        finally:
            if wh is not None:
                wh.close()
if __name__ == "__main__":
    main_test()