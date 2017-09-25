#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

# This is a wrapper for decca-disc.py.  Read the README for
# details.

# imports

import sys
import commands

# -----

try:
    filtertries = sys.argv[1]
except: 
    print "Usage: " + sys.argv[0] + " filtertries.txt"
    sys.exit()


# --------------------------------------------------------
# Read in the constituents and their string equivalents

Counts = {}

try:
    nonterminals = open(filtertries)
except:
    sys.stderr.write("\n\nError: Unable to open filtertries file " + filtertries + "\n")
    sys.exit(1)

line = nonterminals.readline()

while line:
    line = line.strip()
    spl = line.split("\t")

    # remove the index, cat, and binary labels from the line
    index = spl.pop(0)
    cat = spl.pop(0)
    binary = spl.pop(0)

    # the remaining part of the line/spl is the words of the
    # nonterminal
    length = len(spl)
    if Counts.has_key(length):
        Counts[length] += 1
    else:
        Counts[length] = 1

    line = nonterminals.readline()

nonterminals.close()

# find all keys in Counts greater than 1 and add the integer version to
# unitlist
unitlist = []
for key in Counts.keys():
    if int(Counts[key]) > 1:
        unitlist.append(int(key))

# sort the keys and reverse so that the largest n-grams are processed first
unitlist.sort()

for unit in unitlist:
    print commands.getoutput("./decca-disc.py -u "+str(unit)) + "\n"
