#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)


""" decca-pos.py

    Code to calculate all variation n-grams: takes in a corpus in TnT  
    format and writes out n files as described in Dickinson and Meurers
    (2003), "Detecting Errors in Part-of-Speech Annotation" (EACL-03)

    Authors:  Markus Dickinson and Detmar Meurers
    Date:  May 13, 2003
    Paper link:
       http://www.ling.ohio-state.edu/~dm/papers/dickinson-meurers-03.html

"""

# --------------------------------------------------------
# USER SETTINGS
# --------------------------------------------------------

# Please adjust the settings below based on your current system
# configuration and input corpus.

# Token separator (use any string not found in your corpus)
# [We use " ## " by default to separate tokens in a continuous string.
#  Any sequence which does not appear in the corpus will work,
#  but a simple space will not for a corpus which contains
#  multi-word tokens (e.g. "in front of" or "[ mdash")]

tokensep = " ## "
   
# Optional: default filenames to be used if unspecified on command line
# (Files specified on command line will override these settings.)

input_corpus = "/home/user/research/decca/pos/corpus.tt"
destination_dir = "/home/user/research/decca/pos/corpus-output/"
output_file_stem = "ngrams"

# --------------------------------------------------------
# END USER SETTINGS
# --------------------------------------------------------

# import included modules
import getopt
import sys
import os
import commands

# import bsddb
import bsddb

# import included minimized FreqDist
from nltk_freqdist import *

# specify the long options in arglist
arglist = ['corpus=','directory=','file=','help']
# parse the command line call
opts, args = getopt.getopt(sys.argv[1:],"c:d:f:h",arglist)

# Go through the command line options and see if the user specified a
# directory or a corpus, or asked for help

for option, specification in opts:
    if option in ("-d", "--directory"):
        destination_dir = specification
    elif option in ("-c", "--corpus"):
        input_corpus = specification
    elif option in ("-f", "--file"):
        output_file_stem = specification
    elif option in ("-h", "--help"):
        print """
Code to calculate variation n-grams: takes in a corpus in TnT
format and writes out n files to a directory, as described in
Dickinson and Meurers (2003), "Detecting Errors in Part-of-Speech
Annotation" (EACL-03)

Options:

-c/--corpus      specify the (absolute) corpus name
-d/--directory   specify the (absolute) output directory name
-f/--file        specify the base name for the output files
-h/--help        display this help menu
"""
        sys.exit()

# --------------------------------------------------------
# FUNCTIONS

# the function 'get_word_tag' takes a line in TnT format (word '\t'
# tag) and returns the word and tag

def get_word_tag(line):
    spl = line.split('\t')

    try:
        # For tt style:
        word = spl[0]
        tag = spl[1]
    except:
        sys.stderr.write("\n\nError: Incorrectly formatted input corpus.\nThe format expected is 'word \'\t\' tag'.\n")
        sys.stderr.write("Unable to parse line:\n\n" + line + "\n")
        sys.exit(1)

    return word, tag

# the function 'add_to_dict' adds a word and its tag to a given dictionary

def add_to_dict(Dict,word,tag):
    # if the dictionary already has the word, merely increment the tag.
    if Dict.has_key(word):
        Dict[word].inc(tag)
    # otherwise, first create the distribution, then increment the tag.
    else:
        Dict[word] = FreqDist()
        Dict[word].inc(tag)

def to_string(n):

    if (n < 10):
        n_str='00'+str(n)
    elif (n < 100):
        n_str='0'+str(n)
    else:
        n_str=str(n)
    return n_str

# --------------------------------------------------------
# STEP 0: Initialization

# add a trailing "/" if not already there since it's a directory
if destination_dir[len(destination_dir)-1] != "/":
    destination_dir += "/"

# n is the n-gram counter.  We start with unigrams, so we start with 1

n = 1

# initialize Corpus, which will hold the entire corpus indexed from 1
try:
    Corpus = bsddb.btopen(None)
except:
    sys.stderr.write("\n\nError: Unable to open temporary db for corpus\n")
    sys.exit(1)

# initialize index to 1; at the end of the loop index is corpus-size + 1
index = 1

# intialize Dict, which will hold a dictionary keyed by words, accessing
# a frequency distribution of tags
Dict = {}

# --------------------------------------------------------
# STEP 1: Read in corpus

print "Using corpus: "+input_corpus
print "Writing to:   "+destination_dir
sys.stdout.flush()

# concatenate the path name with the file name and a dot for the
# extension, to be used in the rest of the code
destination_dir += output_file_stem + "."

# open the corpus for reading
try:
    corpus_file = open(input_corpus,'r')
except:
    sys.stderr.write("\n\nError: Unable to open " + input_corpus + "\n")
    sys.exit(1)

# tell the reader, we're reading in the corpus (i.e. unigrams)
print "001 grams:",
sys.stdout.flush()

# Read the entire input, storing each word-tag pair in Corpus

# read the first line of the corpus
line = corpus_file.readline()

while line:
    # strip the line of extra newlines, tabs, etc. and split it by tabs
    line = line.rstrip()

    # input is in TnT format:  word \t tag
    word, tag = get_word_tag(line)

    # store the line
    Corpus[str(index)] = word + '\t' + tag

    # add word & tag to dictionary Dict
    add_to_dict(Dict, word, tag)

    # increment counter, i.e. next line in corpus
    index = index + 1

    # read the next line of the corpus
    line = corpus_file.readline()

# We're done reading in the corpus, so close that file:
corpus_file.close()

# At the end of the loop: index = last corpus position + 1

print "read in,",
sys.stdout.flush()

# --------------------------------------------------------
# STEP 2:
# put all the ambiguous unigrams into Grams, indexed by the corpus
# position (i.e. identical to Corpus, but only the ambiguously tagged
# words are included)

# set Grams to be an empty dictionary
try:
    Grams = bsddb.btopen(None)
except:
    sys.stderr.write("\n\nError: Unable to create temporary db for n-grams\n")
    sys.exit(1)

# for every corpus position, see if it has multiple tags.  If so,
# store it in Grams.  If not, delete it from Dict, so after this loop Dict
# will only be left with entries that have multiple tags (making
# printing easier).  Note that this is why we must first check that Dict
# has the key word.

for i,line in Corpus.iteritems():
    spl = line.split('\t')
    word = spl[0]

    if (Dict.has_key(word)):
        if (len(Dict[word].samples()) > 1): # if i has more than one tag 
            Grams[i] = Corpus[i]         # save that line in Grams
        else:
            del Dict[word]

        # note that we are only deleting non-varying occurrences, so all
        # corpus positions with a varying n-gram will be saved.

# --------------------------------------------------------
# STEP 3: loop over increasing longer n-grams until none found

# MAIN LOOP: loop until Grams, which stores all varyingly-tagged
# n-grams, has no more elements -- i.e. there are not n-grams of that
# size which are tagged in multiple ways

while Grams:
    # begin by printing out results for the current n
    print "variations found,",
    sys.stdout.flush()

    n_str = to_string(n)
    filename = destination_dir+n_str
    if os.path.exists(filename):
        sys.stderr.write("\n\nError: Output file " + filename + " already exists.\n")
        sys.exit(1)
    try:
        file = open(filename,'w')
    except:
        sys.stderr.write("\n\nError: Unable to open output file " + filename + "\n")
        sys.exit(1)
    
    # print out all the n-grams in Dict, which will be the varying ones

    for words in Dict.keys():
        line = str(Dict[words].N()) + '\t' + words
        for tags in Dict[words].samples():
            count = Dict[words].count(tags)
            line = line + '\t' + str(count) + '\t' + tags
        file.write(line+'\n')
        del Dict[words]

    # close the file -- we are done writing to this n-gram
    file.close()

    # print out a note to the screen that these n-grams are finished.
    print "written to file,",
    sys.stdout.flush()

    # sort the file using unix sort, output into the file itself
    commands.getstatusoutput("sort -nr "+filename+" -o "+filename)

    print "and file sorted."
    sys.stdout.flush()

    # Increment n: we are now dealing with the next higher n-gram
    n = n + 1

    # (re)initialize Store, which will store the n-grams, indexed by the
    # corpus position of the first element in the n-gram
    try:
        Store = bsddb.btopen(None)
    except:
        sys.stderr.write("\n\nError: Unable to open temporary db for storage\n")
        sys.exit(1)

    # (re)initialize Dict, which will for each n-gram corpus position
    # the tag sequence that occurs for any occurrence of this n-gram
    Dict = {}

    # define n_str as str(n) padded with leading 0s, for output/filenames
    n_str = to_string(n)

    # tell user we're starting work on this n:
    print n_str+" grams:",
    sys.stdout.flush()

    for key,line in Grams.iteritems():
        # make a list from the word and tag strings stored in Grams

        words, tags = get_word_tag(line)

        wordlist = words.split(tokensep)
        taglist = tags.split(tokensep)

        numkey = int(key)

        # if there is something in the corpus one position to the 
        # left of the n-1 gram  and we haven't already created an
        # n-gram at that position, then create it
        if (numkey > 1) and (not Store.has_key(str(numkey-1))):

            # newkey is the index of the first word in this n-gram
            newkey = str(numkey-1)

            # push the previous word in the corpus onto the front of the
            # list and the previous tag, as well

            corpline = Corpus[newkey]
            spl = corpline.split('\t')
            wordlist.insert(0,spl[0])
            taglist.insert(0,spl[1])

            # create strings from the n-gram lists
            wordline = tokensep.join(wordlist)
            tagline = tokensep.join(taglist)

            # store the wordline and tagline, indexed by the position
            # of the first word
            Store[newkey] = wordline + '\t' + tagline

            # add the tags to the words' dictionary slot.
            add_to_dict(Dict,wordline,tagline)

            # pop the first element off both lists, so that when we
            # create an n-gram to the right, we will be dealing with
            # the original n-1 gram
            wordlist.pop(0)
            taglist.pop(0)

        # if there is a position in the corpus to the right of the entire
        # n-gram (last corpus position = index-1 !) and no n-gram has
        # been created at this key, create a new n-gram to the right
        if ((numkey + (n-1)) < index) and (not Store.has_key(key)):

            # newkey will be the position of the *last* token in the
            # n-gram; key will be the position we index the n-gram on,
            # i.e. the starting position
            newkey = str(numkey+(n-1))

            # append the rightmost word and tag onto their lists

            corpline = Corpus[newkey]
            spl = corpline.split('\t')
            wordlist.append(spl[0])
            taglist.append(spl[1])

            # create strings from the lists
            wordline = tokensep.join(wordlist)
            tagline = tokensep.join(taglist)

            # Store the wordline and tagline, indexed by the position
            # of the first word
            Store[key] = wordline + '\t' + tagline

            # add the tags to the words' dictionary slot.
            add_to_dict(Dict,wordline,tagline)
        #key = Grams.next()
    # end for (key in Grams.keys())

    # reinitialize Grams
    Grams.close()
    try:
        Grams = bsddb.btopen(None)
    except:
        sys.stderr.write("\n\nError: Unable to open temporary db for n-grams\n")
        sys.exit(1)

    # print a note to the screen that these n-grams have been indexed.
    print "read in,",
    sys.stdout.flush()

    # loop over the indexed positions in the Store
    for i in Store.keys():

        storeline = Store[i]
        spl = storeline.split('\t')
        
        # get the word n-gram
        words = spl[0]

        # if we have not yet deleted words, then if is a varying
        # n-gram, put it in Grams.  Otherwise, get rid of it from Dict
        if (Dict.has_key(words)):
            if (len(Dict[words].samples()) > 1):
                # Fill the Grams dictionary from the Store one
                Grams[i] = Store[i]
            else:
                del Dict[words]

        del Store[i]

    # end for (i in Store.keys())

    Store.close()

# end while Grams

print "and no variations found."
sys.stdout.flush()

# close corpus files

Corpus.close()
Grams.close()
