#How to configure and run the parser

##Required modules:
The following Python modules need to installed:
 - RDFLib 4.1.2 (https://github.com/RDFLib/rdflib),
 - Grab 0.4.13 (http://grablib.org/),

##Configuration
All configuration settings should be in ``config.py`` file which should be created from ``config.py.example`` by renaming it.

###Input urls
The list of input urls are set as a Python list to ``input_urls`` variable.

###Run

Once you finished with the configuration you need just to execute the following script:

``
python CeurWsPDFParser/spider.py
``

The dataset will be in ``rdfdb.ttl`` file.

#Queries

SPARQL queries created for the Task 2 as translation of [the human readable queries](https://github.com/ceurws/lod/wiki/QueriesTask2) to SPARQL queries using our data model. 
 
#Contacts

Alexander Shipilo (alexandershipilo@gmail.com)

Liubov Kovriguina (lkovriguina@gmail.com)

Fedor Kozlov (kozlovfedor@gmail.com)

Maxim Kolchin (kolchinmax@niuitmo.ru)

Eugene Cherny (eugene.cherny@niuitmo.ru)
