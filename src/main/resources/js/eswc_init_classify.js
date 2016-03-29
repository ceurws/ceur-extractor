/*
 * Experiments with classification - not used.
 */

function processPage(url)
{
	var srcConfig = {
			width: 1200,
			height: 800
	};
	srcConfig.url = url;
	proc.renderPage('FitLayout.CSSBox', srcConfig);

	proc.initAreaTree('FitLayout.Grouping', {});
	proc.apply('FitLayout.Segm.FindLines', {useConsistentStyle: false, maxLineEmSpace: 1.5});
	proc.apply('FitLayout.Segm.HomogeneousLeaves', {});
	//proc.apply('FitLayout.Segm.SuperAreas', {depthLimit: 2});
	proc.apply('Ceur.Tag.Class', {});
	extr.extractInstances(proc.areaTree.root);
	println("Processed " + url + " we have " + extr.count() + " instances");
}

function train()
{
	proc.execInternal('js/train.js');
}

function test()
{
	proc.execInternal('js/test.js');
}

println("ESWC init done.");

//processPage('file:/home/burgetr/git/TestingLayout/test/ceur/volumes/Vol-1317.html');
processPage('http://ceur-ws.org/Vol-1317/');
processPage('http://ceur-ws.org/Vol-1186/');
processPage('http://ceur-ws.org/Vol-1128/');
processPage('http://ceur-ws.org/Vol-1123/');
processPage('http://ceur-ws.org/Vol-1116/');
processPage('http://ceur-ws.org/Vol-1111/');

extr.save('/tmp/out.arff');
println("processing done.");
