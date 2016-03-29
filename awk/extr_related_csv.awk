#! /usr/bin/gawk
#
# To be applied to http://ceur-ws.org
# Extracts the related workshops and prints the relationships as CSV
# (c) Radek Burget 2015
# cat index.html | awk -f extr_related_csv.awk | php -r 'while(($line=fgets(STDIN)) !== FALSE) echo html_entity_decode($line, ENT_QUOTES|ENT_HTML401);' >related.csv

BEGIN {
	curvol="none";
	see=0;
	OFS=",";
}

tolower($0) ~ /name="?vol-[1-9][0-9]*"/ {
	match($0, /Vol-[1-9][0-9]*/);
	curvol = substr($0, RSTART, RLENGTH);
	see=0;
}

tolower($0) ~ /see also/ {
	see=1;
}

tolower($0) ~ /href="?#vol-[1-9][0-9]*"/ {
	if (see) {
		match($0, /Vol-[1-9][0-9]*/);
		relvol = substr($0, RSTART, RLENGTH);
		print curvol, relvol;
	}
}
