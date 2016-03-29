function processAllData()
{
	storage.clearDB();

	var fileReader = console.readFile('/titles_long.csv');
	var array = fileReader.split(',');
	for (var url in array) {
		processPage(array[url]);
	}
}
