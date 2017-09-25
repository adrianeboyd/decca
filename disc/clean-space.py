#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

# This script takes a file name on the command line and prints to standard
# out the contents with each line stripped of leading and trailing whitespace
# and blank lines removed.

import string
import sys

try:
  filename = sys.argv[1]
except: 
  print "Usage: " + sys.argv[0] + " filename"
  sys.exit()

fileh = open(filename)

line = fileh.readline()
while line:
  line = line.strip()

  # only print out non-empty lines
  if line:
    print line

  line = fileh.readline()

fileh.close()
