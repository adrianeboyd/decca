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
    for line in rarray:
      line = line.strip()
      if line:
        print line
    xmldoc.freeDoc()
    result.freeDoc()
    insent = 0
  elif insent == 1:
    sentence += line

xmlfileh.close()
