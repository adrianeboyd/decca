#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2009 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

# XSLT processing for Decca-XML files
#
# This script addresses problems with applying XSLT stylesheets to large
# Decca-XML corpus files.  Instead of reading in the entire corpus file,
# it applies an XSL stylesheet to each sentence found in a Decca-XML
# file.  It's not very smart, so it depends on the fact that the sentence 
# start and end tags appear on separate lines.

import string
import re
import sys
import libxml2
import libxslt

try:
  xslfile = sys.argv[1]
  xmlfile = sys.argv[2]
except:
  print "Usage: " + sys.argv[0] + " xsl-file deccaxml-file"
  sys.exit()

xmlfileh = open(xmlfile)

sentstart = "<sentence "
sentend = "</sentence>"

xmldeclpatt = re.compile("<\?xml.*>")
sentstartpatt = re.compile(sentstart)
sentendpatt = re.compile(sentend)

styledoc = libxml2.parseFile(xslfile)
style = libxslt.parseStylesheetDoc(styledoc)

# read in sentence chunks from deccaxml file and process with xsl
insent = 0
xmldecl = ""
for line in xmlfileh:
  if xmldeclpatt.search(line):
    xmldecl = line.strip()
  if sentstartpatt.search(line):
    sentence = xmldecl + "\n" + line
    insent = 1
  elif sentendpatt.search(line):
    sentence += line
    xmldoc = libxml2.parseDoc(sentence)
    result = style.applyStylesheet(xmldoc, None)
    plainresult = style.saveResultToString(result)
    rarray = plainresult.splitlines()

    words = {}
    words[0] = "ROOT"
    rels = []
    for line in rarray:
        line = line.strip()
	if line:
            lineparts = line.split()
            sentid = lineparts[0]
            words[int(lineparts[1])] = lineparts[2]
            rels.append([lineparts[1]] + lineparts[3:])

    for line in rels:
	depid = int(line[0])
	depword = words[depid]
	for i in range(1, len(line), 2):
	    headid = int(line[i])
	    if words.has_key(headid):
	      headword = words[headid]
	      deprel = line[i+1]

              if headid == 0:
	          binary = "1"
		  print sentid + "_" + str(depid) + "\t" + deprel + "\t" + binary + "\t" + depword
              else:
	          if headid > depid:
	              deprel += "-R"
		      binlen = headid - depid
		      word1 = depword
		      word2 = headword
		      startid = depid
                  else:
	              deprel += "-L"
		      binlen = depid - headid
		      word1 = headword
		      word2 = depword
		      startid = headid

                  binary = "1"
	          for i in range(0, binlen - 1):
	              binary += "0"
	          binary += "1"

	          print sentid + "_" + str(startid) + "\t" + deprel + "\t" + binary + "\t" + word1 + "\t" + word2
       
    xmldoc.freeDoc()
    result.freeDoc()
    insent = 0
  elif insent == 1:
    sentence += line

xmlfileh.close()
