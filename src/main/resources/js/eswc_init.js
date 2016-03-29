function help()
{
	println("");
	println("HELP:");
	println("  console.exit() -- exit console");
	println("  console.browser() -- open the browser gui");
	println("  storage.connect('http://localhost:8080/bigdata/sparql') -- connect a SPARQL endpoint for storing the data");
	println("  processPage('http://ceur-ws.org/Vol-1/') -- process the given page and store the results");
	println("  processAllData() -- process all the data set and store the results");
	println("  processTrainingSet() -- process the SemPub2015 training set and store the results");
	println("  processEvaluationSet() -- process the SemPub2015 evaluations set (includes the training set as well) and store the results");
	println("  transformToDomain() -- transform all the data to the target domain");
	println("");
	println("For accomplishing the SemPub2015 Task1 the following command should be used:");
	println("  processEvaluationSet(); transformToDomain();");
	println("");
	println("This assumes the Blazegraph storage to be running at http://localhost:8080/bigdata. Use storage.connect() to connect another repository.");
	println("After this, the storage should contain the complete extracted data.");
	println("");
}

function processPage(url)
{
	println("");
	println("*** START " + url);

	//rendering
	var srcConfig = {
			width: 2400,
			height: 800
	};
	srcConfig.url = url;
	proc.renderPage('FitLayout.CSSBox', srcConfig);

	//segmentation
	proc.initAreaTree('FitLayout.Grouping', {});
	//proc.apply('FitLayout.Segm.FindLines', {useConsistentStyle: false, maxLineEmSpace: 1.5});
	//proc.apply('FitLayout.Segm.HomogeneousLeaves', {});
	//proc.apply('FitLayout.Segm.SuperAreas', {depthLimit: 2});
	//proc.apply('Ceur.Tag.Class', {});
	proc.apply('FitLayout.Tag.Entities', {});
	proc.apply('Eswc.Tag.All', {});

	//logical tree
	proc.initLogicalTree('CEUR.Logical', {});

	//save the result
	saveCurrentPage();
	println("... DONE");
}

function saveCurrentPage()
{
	storage.saveBoxTree(proc.page);
	storage.saveAreaTree(proc.areaTree, proc.logicalAreaTree, proc.page.sourceURL);
}

function dumpIndex()
{
	console.dumpIndex('/tmp/all.n3');
	console.dumpEditors('/tmp/editors.n3');
}

function transformToDomain()
{
	//import index data
	storage.importTurtleFromResource('related.ttl');
	storage.importTurtle(console.dumpIndex());
	storage.importTurtle(console.dumpEditors());
	//transform index data to domain
	storage.execQueryFromResource('sparql/constructIndex.sparql');
	//transform volume data to domain
	storage.execQueryFromResource('sparql/logicalTree2domain.sparql');
}

storage.connect("http://localhost:9999/blazegraph/sparql");
proc.execInternal('js/eswc_training.js');
proc.execInternal('js/eswc_eval.js');
proc.execInternal('js/eswc_all.js');

println("The console speaks JavaScript. Type help() for help.");

/*processPage('http://ceur-ws.org/Vol-1317/');
processPage('http://ceur-ws.org/Vol-1/');
processPage('http://ceur-ws.org/Vol-1128/');
processPage('http://ceur-ws.org/Vol-1123/');
processPage('http://ceur-ws.org/Vol-1116/');
processPage('http://ceur-ws.org/Vol-1111/');*/
