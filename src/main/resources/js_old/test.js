extr.clear();

processPage('http://ceur-ws.org/Vol-1317/');
/*processPage('http://ceur-ws.org/Vol-1186/');
processPage('http://ceur-ws.org/Vol-1128/');
processPage('http://ceur-ws.org/Vol-1123/');
processPage('http://ceur-ws.org/Vol-1116/');
processPage('http://ceur-ws.org/Vol-1111/');*/
extr.extractInstances(proc.areaTree.root);

extr.save('/tmp/test.arff');
