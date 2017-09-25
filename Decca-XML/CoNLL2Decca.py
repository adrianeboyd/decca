#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2007 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

""" CoNLL2Decca.py

Convert CoNLL-X shared task data format to Decca-XML
"""

import sys
from xml.sax.saxutils import escape

def write_output(outfile, sentences):
    outfileh = open(outfile, 'w')
    outfileh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfileh.write('<treebank xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://decca.osu.edu/schema/Decca-XML.xsd" id="">\n')

    output_head(outfileh, sentences)

    outfileh.write('\t<body>\n')

    sentencekeys = sentences.keys()
    sentencekeys.sort()

    for key in sentencekeys:
      output_sentence(outfileh, sentences[key], key)

    outfileh.write('\t</body>\n</treebank>\n')
    outfileh.close()

def output_head(outfileh, sentences):
    postags = {}
    deprels = {}

    for key, sentence in sentences.iteritems():
        for word in sentence:
	    postags[word[4]] = 1
	    deprels[word[7]] = 1

    outfileh.write('\t<header>\n')
    outfileh.write('\t\t<annotation>\n')
    outfileh.write('\t\t\t<attribute name="form"/>\n')
    outfileh.write('\t\t\t<attribute name="lemma"/>\n')

    outfileh.write('\t\t\t<attribute name="postag">\n')
    postagskeys = postags.keys()
    postagskeys.sort()
    for pos in postagskeys:
        outfileh.write('\t\t\t\t<value name="' + pos + '"/>\n')
    outfileh.write('\t\t\t</attribute>\n')

    outfileh.write('\t\t\t<attribute name="deprel">\n')
    deprelskeys = deprels.keys()
    deprelskeys.sort()
    for dep in deprelskeys:
        outfileh.write('\t\t\t\t<value name="' + dep + '"/>\n')
    outfileh.write('\t\t\t</attribute>\n')

    outfileh.write('\t\t</annotation>\n')
    outfileh.write('\t</header>\n')

def output_sentence(outfileh, sentence, sentid):
    outfileh.write('\t\t<sentence id="' + escape(str(sentid)) + '">\n')
    for word in sentence:
        outfileh.write('\t\t\t<word id="' + escape(word[0]) + '" form="' + escape(word[1]) + '" lemma="' + escape(word[2]) + '" cpostag="' + escape(word[3]) + '" postag="' + escape(word[4]) + '">\n')
	outfileh.write('\t\t\t\t<head id="' + escape(word[6]) + '" deprel="' + escape(word[7]) + '"/>\n')
	outfileh.write('\t\t\t</word>\n')
    outfileh.write('\t\t</sentence>\n')

def main():
    try:
        infile = sys.argv[1]
	outfile = sys.argv[2]
    except:
        print "Usage: " + sys.argv[0] + " input-corpus output-file"
	sys.exit()

    infileh = open(infile)

    sentences = {}

    sentid = 1

    for line in infileh:
      line = line.strip()
      lineparts = line.split()
      if not sentences.has_key(sentid):
          sentences[sentid] = []
      if len(lineparts) > 0:
          sentences[sentid].append(lineparts)
      else:
          sentid += 1

    write_output(outfile, sentences)

if __name__ == "__main__":
    main()
