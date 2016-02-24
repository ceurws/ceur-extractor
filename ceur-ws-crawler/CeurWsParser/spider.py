#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re

from grab.spider import Spider, Task
from grab.tools.logs import default_logging
import rdflib
from rdflib.namespace import FOAF, DC, DCTERMS

from namespaces import BIBO, SWRC, TIMELINE, SWC, SKOS, DBPEDIAOWL
from parsers import WorkshopSummaryParser, WorkshopPageParser, ProceedingsSummaryParser, \
    PublicationParser, ProceedingsRelationsParser, WorkshopAcronymParser, WorkshopRelationsParser, \
    JointWorkshopsEditorsParser, PublicationNumOfPagesParser, EditorAffiliationParser, EditorNameExpandParser
import config


mappings = dict(
    url_mappings={
        r'^http://ceur-ws\.org/*$': 'index',
        r'^http://ceur-ws\.org/Vol-\d+/*$': 'workshop',
        r'^http://ceur-ws\.org/Vol-\d+/.*\.pdf$': 'publication',
    },
    parser_mappings={
        'index': [
            ProceedingsRelationsParser,
            WorkshopSummaryParser,
            WorkshopAcronymParser,
            WorkshopRelationsParser,
            ProceedingsSummaryParser
        ],
        'workshop': [
            WorkshopPageParser,
            EditorAffiliationParser,
            EditorNameExpandParser,
            JointWorkshopsEditorsParser,
            PublicationParser
        ],
        'publication': [
            PublicationNumOfPagesParser,
            # PDFParser
        ]
    }
)


class CEURSpider(Spider):
    def __init__(self):
        Spider.__init__(self, thread_number=1)
        self.setup_grab(timeout=120)
        self.repo = rdflib.Graph(store='default')
        self.repo.bind('foaf', FOAF)
        self.repo.bind('swc', SWC)
        self.repo.bind('skos', SKOS)
        self.repo.bind('swrc', SWRC)
        self.repo.bind('dbpedia-owl', DBPEDIAOWL)
        self.repo.bind('bibo', BIBO)
        self.repo.bind('dcterms', DCTERMS)
        self.repo.bind('dc', DC)
        self.repo.bind('timeline', TIMELINE)

    def load_initial_urls(self):
        """
        task with lower priority will be processed earlier
        :return:
        """
        if self.initial_urls:
            for url in self.initial_urls:
                if re.match(r'^http://ceur-ws\.org/*$', url, re.I):
                    self.add_task(Task('initial', url=url, priority=0))
                else:
                    self.add_task(Task('initial', url=url, priority=1))

    def task_initial(self, grab, task):
        for url_rex in mappings['url_mappings']:
            if re.match(url_rex, task.url, re.I):
                value = mappings['url_mappings'][url_rex]
                if mappings['parser_mappings'][value]:
                    print "[TASK %s] ==== started ====" % task.url
                for parser in mappings['parser_mappings'][value]:
                    p = parser(grab, task, self.repo, spider=self)
                    try:
                        p.parse()
                    except Exception as ex:
                        print "[TASK %s][PARSER %s] Error: %s" % (task.url, parser, ex)
                        import traceback

                        traceback.print_exc()
                if mappings['parser_mappings'][value]:
                    print "[TASK %s] ==== finished ====" % task.url

    def shutdown(self):
        Spider.shutdown(self)
        f = open('rdfdb.ttl', 'w')
        self.repo.serialize(f, format='turtle')
        self.repo.close()


def main():
    default_logging()
    bot = CEURSpider()
    bot.initial_urls = config.input_urls
    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    print(bot.render_stats())


if __name__ == '__main__':
    main()
