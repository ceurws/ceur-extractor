import inspect
import urllib
import config
from urllib2 import HTTPError

from grab.error import DataNotFound
from grab.tools import rex
from rdflib import URIRef


def create_proceedings_uri(volume_number):
    return URIRef("http://ceur-ws.org/Vol-%s/" % volume_number)


def create_publication_uri(proceedings_url, file_name):
    # for the case file name contain the full url TODO check whether proceedings_url was not removed before
    file_name = file_name.replace(proceedings_url, '')
    head, _, _ = file_name.partition('.')  # remove suffix for file .ps, .ps.gz
    return URIRef('%s#%s' % (proceedings_url, head))


def create_conference_uri(conf_acronym, conf_year):
    return URIRef(config.id['conference'] + urllib.quote(conf_acronym + "-" + conf_year))


def find_university_in_dbpedia(graph, tokens):
    values = ' '.join(['"' + token.strip().replace('\n', '') + '"' for token in tokens])
    try:
        results = graph.query("""SELECT DISTINCT ?university {
            VALUES ?search {
                """ + values + """
            }
            ?university a dbpedia-owl:University .
            {
                ?name_uri dbpedia-owl:wikiPageRedirects ?university ;
                    rdfs:label ?label .
            }
            UNION
            { ?university rdfs:label ?label }
            FILTER(STR(?label) = ?search)
        }""")
        return [row[0] for row in results]
    except HTTPError as er:
        print "[ERROR] DBPedia is inaccessible! HTTP code: %s" % er.code
    except:
        pass
    return []


def clean_string(str):
    """
    Removes tabs and newlines from the given string
    """
    if str is None:
        return None
    else:
        return str.replace('\r', '').replace('\n', '')


class NoTemplateError(Exception):
    pass


class Parser:
    def __init__(self, grab, task, graph, failonerror=True, spider=None):
        """
        Args:
            failonerror (boolean): if True, then parse() method doesn't raise NoTemplateError and write() is not called
        """
        self.grab = grab
        self.task = task
        self.graph = graph
        self.data = {}
        self.failonerror = failonerror
        self.spider = spider
        self.step = 1000

    def parse(self):
        parsed = False
        parsed_method = ''
        for method in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name = method[0]
            if method_name.startswith('parse_template_'):
                try:
                    eval('self.' + method_name + '()')
                    parsed = True
                    parsed_method = method_name
                    break
                except DataNotFound:
                    # traceback.print_exc()
                    pass
        if not parsed:
            print "[TASK %s][PARSER %s] proper parser method hasn't been found" % (self.task.url, self.__class__.__name__)
            if self.failonerror:
                raise NoTemplateError("%s" % self.task.url)
        else:
            if config.DEBUG:
                print "[TASK %s][PARSER %s] with %s" % (self.task.url, self.__class__.__name__, parsed_method)
            self.write()

    def write(self):
        raise Exception("Method doesn't have implementation!")

    def write_triples(self, triples):
        if isinstance(triples, list):
            for triple in triples:
                self.graph.add(triple)
                # length = len(triples)
                # print length
                # if length < self.step:
                #     self.graph.addN(triples)
                # else:
                #     for i in range(0, length, self.step):
                #         self.graph.addN(triples[i: i + self.step if i + self.step < length else length])
        elif isinstance(triples, tuple):
            self.graph.add(triples)
        else:
            raise Exception("%s is wrong parameter! Should be a list of tuples or a tuple" % repr(triples))

    @staticmethod
    def rex(body, patterns, flags=0, default=rex.NULL):
        result = None
        lastexception = DataNotFound()
        found = False
        for pattern in patterns:
            try:
                result = rex.rex(body, pattern, flags, default)
                found = True
                if not result:
                    break
            except DataNotFound as dnf:
                lastexception = dnf
        if found:
            return result
        else:
            raise lastexception

    @staticmethod
    def extract_volume_number(url):
        return rex.rex(url, r'.*http://ceur-ws.org/Vol-(\d+).*').group(1)


class ListParser(Parser):
    def __init__(self, grab, task, graph, failonerror=True, spider=None):
        Parser.__init__(self, grab, task, graph, failonerror=failonerror, spider=spider)
        self.list = []

    def extract_list(self):
        raise Exception("Method doesn't have implementation!")

    def parse(self):
        self.extract_list()
        methods = []
        for method in inspect.getmembers(self, predicate=inspect.ismethod):
            if method[0].startswith('parse_template_'):
                methods.append(method[0])
        if not self.list:
            print "[TASK %s][PARSER %s] nothing to extract!" % (self.task.url, self.__class__.__name__)
        for element in self.list:
            try:
                parsed = False
                parsed_method = ''
                for method in methods:
                    try:
                        eval('self.%s(element)' % method)
                        parsed = True
                        parsed_method = method
                        break
                    except DataNotFound:
                        # traceback.print_exc()
                        pass
                if not parsed:
                    print "[TASK %s][PARSER %s] proper parser method hasn't been found" % (self.task.url, self.__class__.__name__)
                    if self.failonerror:
                        raise NoTemplateError("%s" % self.task.url)
                else:
                    if config.DEBUG:
                        print "[TASK %s][PARSER %s] with %s" % (self.task.url, self.__class__.__name__, parsed_method)
                    self.write()
            except NoTemplateError:
                print "[PARSER %s] Can't parse %s" % (self.__class__.__name__, element)
