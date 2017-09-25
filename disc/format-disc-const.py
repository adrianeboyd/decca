#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

# This script takes the input corpus and the output from applying 
# tigerxml-constituents.xsl to the TIGER-XML corpus and converts it to 
# the constituents input file needed by decca-disc.py.

import sys
import bsddb

try:
    corpus_filename = sys.argv[1]
    tempcons_filename = sys.argv[2]
except: 
    print "Usage: " + sys.argv[0] + " input_corpus.txt temp_cons.txt"
    sys.exit()

try:
    corpus_fileh = open(corpus_filename)
except:
    sys.stderr.write("\n\nError: Unable to open corpus file " + corpus_filename + "\n")
    sys.exit(1)

try:
    tempcons_fileh = open(tempcons_filename)
except:
    sys.stderr.write("\n\nError: Unable to open temp_cons file " + tempcons_filename + "\n")
    sys.exit(1)

# read in the corpus and set each "s#_#" value to its corresponding global
# corpus position (token count from beginning of corpus)
Corpus = bsddb.btopen(None)

i = 1
line = corpus_fileh.readline()
while line:
    line = line.strip()
    (id,word,tag) = line.split('\t')
     
    Corpus[id] = str(i)

    # iterate i and get the next line
    i = i + 1
    line = corpus_fileh.readline()

corpus_fileh.close()

line = tempcons_fileh.readline()
while line:
  line = line.strip()

  # only process non-empty lines
  if line:
    linearray = line.split('\t')
    cat = linearray[0]
    terminals = linearray[1:]
    sentnum = linearray[1].split('_')[0][1:]

    # create a hash with the terminals keyed by position (to be able to
    # generate the output with the terminals in order in case they were
    # not in order in the input file)
    orderedterms = {}
    for index in range(0, len(terminals), 2):
      label = terminals[index]
      labelarray = label.split('_')
      wordnum = int(labelarray[1])
      word = terminals[index+1]
      orderedterms[wordnum] = word

    orderedtermkeys = orderedterms.keys()
    orderedtermkeys.sort()

    # look up the global corpus position of the first terminal in this
    # constituent
    catstart = Corpus["s" + sentnum + "_" + str(orderedtermkeys[0])]

    # the output starts with the global position and the category
    output = catstart + "\t" + cat

    # create the left-to-right binary string for this constituent
    prev_pos = orderedtermkeys[0]
    for key in orderedtermkeys:
      if prev_pos == key:
        binstring = "1"
      elif prev_pos == key - 1:
        binstring += "1"
      else:
        while prev_pos < key - 1:
	  binstring += "0"
	  prev_pos += 1
	binstring += "1"

      prev_pos = key

    # add the binary string to the output
    output += "\t" + binstring

    # add the terminals in order to the output
    for key in orderedtermkeys:
      output += "\t" + orderedterms[key]  

    print output

  line = tempcons_fileh.readline()

Corpus.close()
tempcons_fileh.close()
