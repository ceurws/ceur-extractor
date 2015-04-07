from datetime import datetime
import re
import urllib

from grab.spider import Task
from grab.tools import rex, text
from grab.error import DataNotFound
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, DCTERMS, DC, SKOS

from namespaces import SWRC
from base import Parser, create_proceedings_uri
import config

XPATH_SUMMARY = '/html/body/table[position()>1]//tr[td]'

class ProceedingsSummaryParser(Parser):
    XPATH_SUMMARY_TITLE = './/td[last()]//a[@href]'

    def parse_template_main(self):
        proceedings_list = []
        tr = self.grab.tree.xpath(XPATH_SUMMARY)
        for i in range(0, len(tr), 2):
            href = tr[i].find(self.XPATH_SUMMARY_TITLE)
            try:
                if href.get('href') in config.input_urls or len(config.input_urls) == 1:
                    proceedings = dict()
                    proceedings['volume_number'] = ProceedingsSummaryParser.extract_volume_number(href.get('href'))
                    proceedings['url'] = href.get('href')
                    summary_match = rex.rex(
                        tr[i + 1].find('.//td[last()]').text_content(),
                        r'(.*)(\nEdited\s*by\s*:\s*)(.*)(\nSubmitted\s*by\s*:\s*)(.*)(\nPublished\s*on\s*CEUR-WS:\s*)(.*)(\nONLINE)(.*)',
                        re.I | re.M | re.S)

                    proceedings['label'] = re.sub(r'\n', '', text.normalize_space(summary_match.group(1), ' \n'))
                    proceedings['editors'] = re.split(r",+\s*", text.normalize_space(summary_match.group(3)))
                    proceedings['submission_date'] = datetime.strptime(
                        text.normalize_space(summary_match.group(7), ' \n'),
                        '%d-%b-%Y')

                    proceedings_list.append(proceedings)
            except:
                print "[WORKSHOP %s: ProceedingsSummaryParser] Summary information not found!" % href.get('href')
                #traceback.print_exc()

        self.data['proceedings_list'] = proceedings_list

        if len(proceedings_list) == 0:
            raise DataNotFound("There is no summary information to parse!")

    def write(self):
        triples = []
        for proceedings in self.data['proceedings_list']:
            resource = URIRef(proceedings['url'])
            triples.append((resource, RDF.type, SWRC.Proceedings))
            triples.append((resource, SWRC.title, Literal(proceedings['label'], datatype=XSD.string)))
            triples.append((resource, FOAF.homepage, Literal(proceedings['url'], datatype=XSD.anyURI)))
            triples.append((
                resource,
                DCTERMS.issued,
                Literal(proceedings['submission_date'].strftime('%Y-%m-%d'), datatype=XSD.date)))
            for editor in proceedings['editors']:
                agent = URIRef(config.id['person'] + urllib.quote(editor.encode('utf-8')))
                triples.append((agent, RDF.type, FOAF.Person))
                triples.append((agent, FOAF.name, Literal(editor, datatype=XSD.string)))
                triples.append((resource, SWRC.editor, agent))
                triples.append((resource, FOAF.maker, agent))
                triples.append((agent, FOAF.made, resource))

        self.write_triples(triples)


class ProceedingsRelationsParser(Parser):
    """
    Should parser the index page before WorkshopSummaryParser parser, because this parser updates config.input_urls.

    WARNING: Ignores joint proceedings!
    """

    def parse_template_main(self):
        tr = self.grab.tree.xpath(XPATH_SUMMARY)
        self.data['proceedings'] = []
        for i in range(0, len(tr), 2):
            proceedings_url = tr[i].find('.//td[last()]//a[@href]').get('href')
            if len(config.input_urls) == 1:
                self.spider.add_task(Task('initial', url=proceedings_url))
            if proceedings_url in config.input_urls or len(config.input_urls) == 1:
                related = []
                for a in tr[i + 1].findall(".//td[1]//a[@href]"):
                    if len(a.get('href')) > 1:
                        related.append(a.get('href')[5:])
                proceedings = {
                    'volume_number': ProceedingsRelationsParser.extract_volume_number(proceedings_url),
                    'related': related
                }
                self.data['proceedings'].append(proceedings)

    def write(self):
        triples = []
        for proceedings in self.data['proceedings']:
            if len(proceedings['related']) > 0:
                resource = create_proceedings_uri(proceedings['volume_number'])
                for related in proceedings['related']:
                    related_url = "http://ceur-ws.org/Vol-%s/" % related
                    if len(config.input_urls) > 1 and related_url not in config.input_urls:
                        config.input_urls.append(related_url)
                    #     # self.spider.add_task(Task('initial', url=related_url))

                    related_resource = create_proceedings_uri(related)
                    triples.append((resource, RDFS.seeAlso, related_resource))
        self.write_triples(triples)
