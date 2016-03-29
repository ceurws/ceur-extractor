#! /usr/bin/gawk
#
# To be applied to http://ceur-ws.org
# Extracts the editors for the individual volumes
# (c) Radek Burget 2015
#

#Decode entities:
#cat index.html | awk -f extr_editors.awk | php -r 'while(($line=fgets(STDIN)) !== FALSE) echo html_entity_decode($line, ENT_QUOTES|ENT_HTML401);' >editors.n3

function ltrim(s) { sub(/^[ \t\r\n]+/, "", s); return s }
function rtrim(s) { sub(/[ \t\r\n]+$/, "", s); return s }
function trim(s)  { return rtrim(ltrim(s)); }
function clean(s) { sub(/<[A-Za-z]+>/, "", s); return s }

BEGIN {
	curvol = "none";
	OFS = " segm:editorname ";
	eds = "";
	ineds = 0;
}

tolower($0) ~ /name="?vol-[1-9][0-9]*"/ {
	match($0, /Vol-[1-9][0-9]*/);
	curvol = substr($0, RSTART, RLENGTH);
	eds = "";
	ineds = 0;
	next
}

tolower($0) ~ /^edited by:/ {
	match($0, /:.+$/);
	eds = substr($0, RSTART+1, RLENGTH-1);
	ineds = 1;
	next
}

/\:/ {
	if (ineds == 1) {
	  #print curvol, eds;
	  n = split(trim(eds), t, ",")
	  for (i = 1; i <= n; i++) {
	      print "<http://ceur-ws.org/" curvol "/>", "\"" trim(clean(t[i])) "\" ."
	  }
	}
	ineds = 0;
	next
}

/.*/ {
	if (ineds == 1) {
	  eds = (eds $0);
	}
}
