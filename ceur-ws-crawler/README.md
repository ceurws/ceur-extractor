#How to configure and run the parser

##Prerequisites
The following Python modules need to be installed:
 - RDFLib 4.1.2 (https://github.com/RDFLib/rdflib),
 - PDFMiner 20140328 (http://www.unixuser.org/~euske/python/pdfminer/),
 - Grab 0.4.13 (http://grablib.org/),
 - PyPDF2 1.23 (https://github.com/mstamy2/PyPDF2),
 - FuzzyWuzzy (https://github.com/seatgeek/fuzzywuzzy),
 - Python-Levenshtein (https://pypi.python.org/pypi/python-Levenshtein)

You can install them by using the requirements.txt software list with the following command
##### sudo pip install -r requirements.txt

To start the reasoner you will need Java 1.7 and Maven.

##Configuration
All configuration settings should be in ``config.py`` file which should be created from ``config.py.example`` by renaming it.

###Input urls
The list of input urls are set as a Python list to ``input_urls`` variable.

###DBpedia dataset (with countries and universities)
Parser uses [DBpedia](http://dbpedia.org/) to extract the names of countries and univeristies, and their URIs in DBpedia.

There are three options:
 - to use the original dataset. It's by default, nothing should be configured,
 - to use the [OpenLink's mirror](http://dbpedia.org/), then the ``sparqlstore['dbpedia_url']`` should be changed to ``http://lod.openlinksw.com/sparql``,
 - to use a local dump, it's prefered option, because it should be much faster and more stable. The ``sparqlstore['dbpedia_url']`` should be set to the local SPARQL Endpoint and the RDF files ``dumps/dbpedia_country.xml`` and ``dumps/dbpedia_universities.xml`` should be uploaded to it. Look at [the wiki](https://github.com/ailabitmo/sempubchallenge2014-task1/wiki/How-to-construct-the-DBpedia-dumps) to find the steps to generate the DBpedia dumps.

###Run

Once you have finished with the configuration you need to execute the following commands
(provided that you are in the ``ceur-ws-crawler`` directory):

```bash
python CeurWsParser/spider.py
mvn package -f reasoner
java -jar reasoner/target/reasoner-1.0-SNAPSHOT-jar-with-dependencies.jar rdfdb.ttl alignments.ttl rdfdb_reasoned.ttl
python postprocessing/merge_persons.py rdfdb_reasoned.ttl
python postprocessing/merge_ttls.py rdfdb_reasoned.ttl persons_sameas.ttl
```

The dataset will be in ``sempub2015-task1.ttl`` file.

#Queries

SPARQL queries created for the Task 1 as translation of [the human readable queries](http://challenges.2014.eswc-conferences.org/index.php/SemPub/Task1#Queries) to SPARQL queries using our [data model](https://github.com/ailabitmo/sempubchallenge2014-task1/wiki/Data-representation). The queries are in [the wiki](https://github.com/ailabitmo/sempubchallenge2014-task1/wiki/Queries).
