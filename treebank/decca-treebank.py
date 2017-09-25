#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)


""" decca-treebank.py

    Code to calculate all variation n-grams: takes in a corpus
    (input_corpus) in line-by-line format, as well as a text file of all
    the constituents in a corpus (constituents), indexed by position,
    and writes out n files as described in Dickinson and Meurers (2003)
    "Detecting Inconsistencies in Treebanks" (TLT 2003)

    Authors:  Markus Dickinson and Detmar Meurers
    Date:  September 3, 2003
    Paper link:
       http://www.ling.ohio-state.edu/~dm/papers/dickinson-meurers-tlt03.html

"""

# --------------------------------------------------------
# USER SETTINGS
# --------------------------------------------------------

# Token separator (use any string not found in your corpus)
# [We use " ## " by default to separate tokens in a continuous string.
#  Any sequence which does not appear in the corpus will work,
#  but a simple space will not for a corpus which contains
#  multi-word tokens (e.g. "in front of" or "[ mdash")]

tokensep = " ## "

# the character encoding is used for the XHTML output

charencoding = "iso-8859-1"

# Optional: default parameters to be used if unspecified on command line
# (Files specified on command line will override these settings.)

input_corpus = "/home/user/research/decca/treebank/corpus.txt"
cached_corpus = "/home/user/research/decca/treebank/corpus.bsddb"
constituents = "/home/user/research/decca/treebank/corpus.constituents"
cached_cons = "/home/user/research/decca/treebank/corpus.cons.bsddb"
destination_dir = "/home/user/research/decca/treebank/output/"
output_file_stem = "corpus-grams"

# unit is the window we are examining -- i.e. the length of the string
# covered by a nonterminal

unit = 3

# use plaintext output: 0, xhtml: 1
xhtml = 0

# --------------------------------------------------------
# END USER SETTINGS
# --------------------------------------------------------

# import included modules
import getopt
import sys
import os
import commands

# import extra modules
import bsddb

from nltk_freqdist import *

# specify the long options in arglist
arglist = ['unit=','corpus=','cached-corp=','constituents=','cached_const=','directory=','xhtml','file=','help'] 
# parse the command line call
opts, args = getopt.getopt(sys.argv[1:],"u:c:b:d:o:n:x:f:h",arglist)

# Go through the command line options and see if the user specified a
# directory or a corpus, or asked for help

for option, specification in opts:
    if option in ("-u", "--unit"):
        strunit = specification
        unit = int(strunit)
    if option in ("-d", "--directory"):
        destination_dir = specification
    elif option in ("-c", "--corpus"):
        input_corpus = specification
    elif option in ("-b", "--cached-corp"):
        cached_corpus = specification;
    elif option in ("-o", "--constituents"):
        constituents = specification
    elif option in ("-n", "--cached-const"):
        cached_constituents = specification;
    elif option in ("-x", "--xhtml"):
        if xhtml == 1:
	    newxhtml = 0
	elif xhtml == 0:
            newxhtml = 1
	xhtml = newxhtml
    elif option in ("-f", "--file"):
        output_file_stem = specification
    elif option in ("-h", "--help"):
        print """

Code to calculate all variation n-grams: takes in a corpus
(input_corpus) in line-by-line format, as well as a text file of all
the constituents in a corpus (constituents), indexed by position,
and writes out n files to destination_dir.

Options:

-u/--unit          specify the unit length
-c/--corpus        specify the (absolute) corpus file name
-b/--cached-corp   specify the (absolute) cached corpus file name
-o/--constituents  specify the (absolute) constituents file name
-n/--cached-const  specify the (absolute) cached constituents file name
-d/--directory     specify the (absolute) output directory name
-f/--file          specify the base name for the output files
-x/--xhtml         toggle XHTML output
-h/--help          display this help menu
"""
        sys.exit()

# add a trailing "/" if not already there since it's a directory
if destination_dir[len(destination_dir)-1] != "/":
    destination_dir += "/"

# create output string for unit setting
unit_str = str(unit)
if unit < 10:
    unit_str = "0" + unit_str

# print output settings
if xhtml:
    print "Generating XHTML output."
else:
    print "Generating plain text output."

# create output directory if it doesn't exist
if not os.path.exists(destination_dir):
    print commands.getoutput("mkdir " + destination_dir)
    print "Creating directory " + destination_dir
if not os.path.exists(destination_dir + unit_str):
    print commands.getoutput("mkdir " + destination_dir + unit_str)
    print "Creating directory " + destination_dir + unit_str

# concatenate the path name with the file name and a dot for the
# extension, to be used in the rest of the code
destination_dir += unit_str + "/" + output_file_stem + "."

# --------------------------------------------------------

def get_n_str(n,unit):
    # define n_str as str(n) padded with leading 0s, for
    # output/filenames.  "n_str" is actually n+unit-1, given the way the
    # variable n is defined
    if (n+unit-1 < 10):
        n_str='00'+str(n+unit-1)
    elif (n+unit-1 < 100):
        n_str='0'+str(n+unit-1)
    else:
        n_str=str(n+unit-1)
    return n_str

def add_to_dict(Dict,words,offset,cat):
    if (Dict.has_key(words)):
        if Dict[words].has_key(offset):
            Dict[words][offset].inc(cat)
        else:
            Dict[words][offset] = FreqDist()
            Dict[words][offset].inc(cat)
    else:
        Dict[words] = {}
        Dict[words][offset] = FreqDist()
        Dict[words][offset].inc(cat)

def print_output(Output,filename):
    if xhtml:
        filename += ".html"

    if os.path.exists(filename):
        sys.stderr.write("\n\nError: Output file " + filename + " already exists.\n")
        sys.exit(1)
    try:
        file = open(filename,'w')
    except:
        sys.stderr.write("\n\nError: Unable to open file " + filename + "\n")
	sys.exit(1)

    if xhtml:
        file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        file.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n')
        file.write("<head><title>" + os.path.basename(filename) + "</title>\n")
        file.write('<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=' + charencoding + '" />\n')
        file.write('<meta http-equiv="content-language" content="en" />\n')
        file.write("</head>\n<body>\n")

    okeys = Output.keys()
    okeys.sort()
    okeys.reverse()

    for key in okeys:
        for line in Output[key]:
	  file.write(line + "\n")

    if xhtml:
	file.write("</body>\n</html>\n")

    file.close()

def gen_output(Dict,xhtml):
    Output = {}

    # --------
    # GENERATING OUTPUT
    # find all the n-grams in Dict, which will be the varying ones

    for words in Dict.keys():
	line = words
	total = 0

	if xhtml:
	    line += "</p>\n"
	    line += "<ul>\n"

        # nb: the total should be the same for all offsets
        for offset in Dict[words].keys():
            
            if (Dict[words][offset].N()> total):
                total = Dict[words][offset].N()
                
            if xhtml:
	        line += "<li>" + str(offset) + " <ul>\n"
		for cat in Dict[words][offset].samples():
                    count = Dict[words][offset].count(cat)
                    line += "<li>" + str(count) + ': ' + cat + "</li>\n"
		line += "</ul>\n</li>\n"
	    else:
                # add the count of the cat@offset along with offset
                # position (in parentheses)
                line = line + '\t' + ' (' + str(offset) + ') --'
            
                # for all cats (the actual variation), print them out with
                # their counts
                for cat in Dict[words][offset].samples():
                    count = Dict[words][offset].count(cat)
                    line = line + '  ' + str(count) + ':' + cat

            del Dict[words][offset]


        if xhtml:
            line = "<p>" + str(total) + ": " + line + "</ul>"
	else:
            line = str(total) + "\t" + line

        if not Output.has_key(total):
	    Output[total] = []
	Output[total].append(line)
        del Dict[words]
        
    return Output

def handle_one_line(line):
    spl = line.split('\t')
    # pop the words off the back of the list
    words = spl.pop()

    pairlist = []

    while spl:
        pair = spl.pop()
        newspl = pair.split(':')
        if newspl[0]:
            offset = int(newspl[0])
        else:
            offset = 99999
        cat = newspl[1]
        pairlist.append((offset,cat))
    return words, pairlist

def have_seen(some_offset,newpairlist):
    seen = 0
    for (this_offset,this_cat) in newpairlist:
        if int(some_offset) == this_offset:
            seen = 1
    return seen

# --------------------------------------------------------

# we are working with the base case "unit-grams", so we set n to be 1
# (they can be thought of as essentially unigrams)

n = 1

print "Working with window units of length " + str(unit)

# --------------------------------------------------------
# STEP 1: Read in nonterminals

print "Using corpus: " + input_corpus
print "Writing to:   " + destination_dir
sys.stdout.flush()


# tell the reader, we're reading in the corpus (i.e. unigrams)
n_str = get_n_str(n,unit)
print n_str + " grams:",
sys.stdout.flush()

# create Dict, the dictionary of variations
Dict = {}

Grams = bsddb.btopen(None)

# open up the file which contains all the nonterminal stretches of text

if not os.path.exists(cached_cons):
    try:
        nonterminals = open(constituents,'r')
    except:
        sys.stderr.write("\n\nError: Unable to open constituents file " + constituents + "\n")
        sys.exit(1)
    j = 1
    Constituents = bsddb.btopen(cached_cons)
    line = nonterminals.readline()
    while line:
        line = line.strip()
	Constituents[str(j)] = line
	j = j + 1
	line = nonterminals.readline()
    nonterminals.close()
    print "nonterminals read in and cached,",
else:
    Constituents = bsddb.btopen(cached_cons)
    print "cached nonterminals read in,",
sys.stdout.flush()

for key in range(1, len(Constituents.keys()) + 1):
    line = Constituents[str(key)]
    spl = line.split("\t")

    # we only want to deal with windows of unit length (unit+2 because
    # of the index and cat labels)
    if (len(spl) == unit + 2):
        index = spl.pop(0)
        cat = spl.pop(0)

        span = tokensep.join(spl)

        # Grams will be in the form:
        # "offset1:cat1\t...\toffsetN:catN\twords"
        # where offseti is the offset point of the n-gram where cat_i
        # starts (in the base case, all offsets are 0 because they
        # start at the beginning

        if Grams.has_key(index):
            templine = Grams[index]

            words, pairlist = handle_one_line(templine)

            # pairlist should be length 1
            for (old_offset,oldcat) in pairlist:

                # a cat that accounts for a unary branch will be longer
                # than one that does not, so we want to keep it
            
                if len(cat) > len(oldcat):
                    Grams[index] = "0:" + cat + '\t' + span
        else:
            Grams[index] = "0:" + cat + '\t' + span

# we now loop over Grams to store the n-grams in a dictionary (Dict),
# which will be used to keep track of varying n-grams

for index, line in Grams.iteritems():
    # get the cat and actual n-gram (span) from Grams for this index

    span, pairlist = handle_one_line(line)

    # pairlist should be length 1 and offset should be 0
    for (offset,cat) in pairlist:

        # Dict will be in the form:
        # Dict[span] = {offset:<FreqDist of cats>, ...}

        add_to_dict(Dict,span,offset,cat)

# --------------------------------------------------------
# STEP 2:  Read in corpus

# set the corpus counter to be 1, the start of the corpus
i = 1

# initialize Corpus, which will hold the entire corpus indexed from 1
# if the corpus has already been cached, read it in, otherwise read the
# input_corpus and save as the cached_corpus
if not os.path.exists(cached_corpus):
    try:
        corpus_file = open(input_corpus,'r')
    except:
        sys.stderr.write("\n\nError: Unable to open corpus file " + input_corpus + "\n")
        sys.exit(1)
    Corpus = bsddb.btopen(cached_corpus)
    line = corpus_file.readline()
    while line:
        line = line.rstrip()
        (id,word,tag) = line.split('\t')
    
        Corpus[str(i)] = word + '\t' + tag

        # iterate i and get the next line
        i = i + 1
        line = corpus_file.readline()

    corpus_file.close()
    print "corpus read in and cached,",
    sys.stdout.flush()
else:
    Corpus = bsddb.btopen(cached_corpus)
    print "cached corpus read in,",
    sys.stdout.flush()

# set index to be the length of the corpus (plus 1)
index = len(Corpus.keys()) + 1

# ngram is a list which allows us to build up our unit-grams
ngram = []

# Going through the corpus word by word, compare the n-grams we create
# with the nonterminal ones we already have and add new ones to Grams and
# Dict -- i.e. ones that are the same string but have no single nonterminal 
# yield

for i in range(1, index):
    line = Corpus[str(i)]
    (word,tag) = line.split('\t')
    
    # we must build up the current n-gram.  To do so, we have to append
    # until we reach that n-gram level
    if (i < unit):
        ngram.append(word)
    else:
        ngram.append(word)
        ngramstring = tokensep.join(ngram)

        # since Grams is indexed by the start position of the n-gram,
        # we have to calculate that start position (since we are at the
        # end of the n-gram currently)
        start = str(i - unit + 1)

        # if Grams has the start key, then we already know the cat label
        # for the n-gram, so ignore it.
        # But if it is not -- AND it appears elsewhere with a non-nil cat
        # label (i.e. is in Dict) -- then put it in Grams and Dict

        if (not Grams.has_key(start)) and (Dict.has_key(ngramstring)):
            Grams[start] = '0:NIL' + '\t' + ngramstring
            Dict[ngramstring][0].inc('NIL')

        # note that we ignore all stretches that have no nonterminal
        # yield anywhere in the corpus -- obviously, they will not
        # vary
            
        # pop off the first element for the next loop
        ngram.pop(0)


# --------------------------------------------------------

# filter out the nonvariations in Grams

for key in Grams.keys():
    line = Grams[key]
    spl = line.split('\t')
    words = spl.pop()
    
    if Dict.has_key(words) and (len(Dict[words][0].samples()) < 2):
        del Grams[key]
        del Dict[words]
    elif not Dict.has_key(words):
        # Dict[words] has already been deleted
        del Grams[key]
    else:
        sys.stderr.write(key + "\n")

# --------------------------------------------------------
# NOW BEGINS THE (non-base case) A PRIORI WORK

# Grams[i] = offset1:cat\ t ... \t offsetN:cat \t words
# Dict[words] = {offset1:<FreqDist>, ..., offsetN:<FreqDist>}

# --------------------------------------------------------
# STEP 3: loop over increasing longer n-grams until none found

# MAIN LOOP: loop until Grams, which stores all varyingly-tagged
# n-grams, has no more elements -- i.e. there are not n-grams of that
# size which are tagged in multiple ways

while Grams:
    # write results for current n

    print "variations found,",
    sys.stdout.flush()

    filename = destination_dir+n_str
    Output = gen_output(Dict,xhtml)
    print_output(Output,filename)

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
    Store = {}

    # (re)initialize Dict, which will for each n-gram corpus position
    # store the tag sequence that occurs for any occurrence of this
    # n-gram
    Dict = {}

    n_str = get_n_str(n,unit)

    # tell user we're starting work on this n:
    print n_str+" grams:",
    sys.stdout.flush()

    # Grams holds all the n-1 grams in string form, so we cycle through them.
    for key, line in Grams.iteritems():

        (words, pairlist) = handle_one_line(line)

        # we have to iterate through pairlist, the list of all offset
        # positions, in order to find all larger n-grams that have
        # variation starting at that offset        
        for (old_offset, cat) in pairlist:

            # make a list out of words, so we can easily add and
            # subtract words from it (to the right and left)
            wordlist = words.split(tokensep)

            # get the integer form of key, so we can manipulate it
            numkey = int(key)

            # ------------------
            # EXPAND TO THE LEFT

            # if there is something in the corpus one position to the
            # left of the n-1 gram (numkey > 1), then if Store has
            # this key, see if it also has the offset

            if (numkey > 1):

                # get the newkey and the new_offset values (when the
                # key moves to the left, new_offset increases by 1
                newkey = str(numkey-1)
                new_offset = str(old_offset+1)

                # check to see if this string has been generate before
                if Store.has_key(newkey):

                    # get the Stored value for this key
                    newline = Store[newkey]
                    newwords, newpairlist = handle_one_line(newline)
                    seen = have_seen(new_offset,newpairlist)

                    # we have not seen new_offset, so add it to Store
                    if not seen:
                        newstoreline = new_offset + ":" + cat + "\t" + newline
                        Store[newkey] = newstoreline

                        # add the tags to the words' dictionary slot.
                        add_to_dict(Dict,newwords,new_offset,cat)
                    else:
                        Store[newkey] = newline

                # not Store.has_key(newkey) -->
                # now we know that we have not seen this new_offset or
                # even this n-gram starting at numkey-1
                else:

                    # since we have not seen this n-gram, we must add it a
                    # word from the corpus to the left
		    corpusline = Corpus[newkey]
                    (corpline,corptag) = corpusline.split('\t')
                    wordlist.insert(0,corpline)

                    # create strings from the n-gram lists
                    wordline = tokensep.join(wordlist)

                    # store the wordline and offset, indexed by the position
                    # of the first word (newkey)
                    Store[newkey] = new_offset + ":" + cat + '\t' + wordline

                    # add the offsets and corresponding cats to the words'
                    # dictionary slot.
                    add_to_dict(Dict,wordline,new_offset,cat)

                    # pop the first element off both lists, so that
                    # when we create an n-gram to the right, we will
                    # be dealing with the original n-1 gram
                    wordlist.pop(0)

            # -------------------
            # EXPAND TO THE RIGHT

            # if there is a position in the corpus to the right of
            # the entire n-gram (last corpus position = index-1)
            # and no n-gram has been created at this key, create a
            # new n-gram to the right
            if ((numkey + (unit-1) + (n-1)) < (index-1)):

                # a little unpacking of (numkey + (unit-1) + (n-1)):
                # numkey is the starting key of the string
                
                # n is the variation n-gram we are working with.
                # So, numkey + (n-1) gives us the final word of this
                # n-gram (the first word + n-1 = n)

                # But these "words" are not atomic units, rather they
                # are stretches of length unit.  So, we need to get
                # the length of the "word" before adding n-1 -- the
                # length will be 1 + unit-1, so we add (unit-1)

                # the offset stays the same because we extend to the right
                newkey = str(numkey+(unit-1)+(n-1))
                new_offset = str(old_offset)

                if Store.has_key(key):

                    # get the Stored value of this key
                    newline = Store[key]
                    newwords,newpairlist = handle_one_line(newline)
                    seen = have_seen(new_offset,newpairlist)
                
                    # we have not seen new_offset, so add it to Store
                    if not seen:
                        newstoreline = new_offset + ":" + cat + "\t" + newline
                        Store[key] = newstoreline

                        # add the tags to the words' dictionary slot.
                        add_to_dict(Dict,newwords,new_offset,cat)
                    else:
                        Store[key] = newline

                # not Store.has_key(key) -->
                # now we know that we have not seen this new_offset or
                # even this n-gram starting at numkey
                else:

                    # since we have not seen this n-gram, we must add it a
                    # word from the corpus to the right
		    corpusline = Corpus[newkey]
                    (corpline,corptag) = corpusline.split('\t')
                    wordlist.append(corpline)

                    # create strings from the n-gram lists
                    wordline = tokensep.join(wordlist)

                    # store the wordline and tagline, indexed by the position
                    # of the first word (key)
                    Store[key] = new_offset + ":" + cat + '\t' + wordline

                    # add the tags to the words' dictionary slot.
                    add_to_dict(Dict,wordline,new_offset,cat)

                    wordlist.pop()
                        
    # end for (key in Grams.keys())

    # reinitialize Grams
    Grams.close()
    Grams = bsddb.btopen(None)

    # print a note to the screen that these n-grams have been indexed.
    print "read in,",
    sys.stdout.flush()

    # ----------------------------
    # FILTER OUT THE NON-VARIATIONS

    # loop over the indexed positions in the Store
    for i in Store.keys():
        # get the Store's i'th value
        storeline = Store[i]
        words, pairlist = handle_one_line(storeline)

        # if 'words' is a varying n-gram, put it in Grams.  Otherwise,
        # get rid of it from Dict
        if (Dict.has_key(words)):

            # set variation to 0; we will see if any of the offsets
            # are varying.  If so, we keep it (otherwise, delete
            # offsets that result in no variation)
            variation = 0
            for offset in Dict[words].keys():
                if len(Dict[words][offset].samples()) > 1:
                    variation = 1
                else:
                    del Dict[words][offset]

            # if at least one of the offsets provided variation, we
            # add this i'th value of Store to Grams; otherwise, delete
            # it            
            if (variation == 1):
                # Fill the Grams dictionary from the Store one

                # we need to eliminate non-varying offsets from
                # storeline when we put it into Grams

                gramline = ""
                for (offset,cat) in pairlist:
                    pair = str(offset) + ":" + cat
                    
                    if Dict[words].has_key(str(offset)):
                        # put the pair into the gramline only if words
                        # has variation at this spot
                        if gramline:
                            gramline = gramline + "\t" + pair
                        else:
                            gramline = pair
                if gramline:
                    gramline = gramline + "\t" + words
                    Grams[i] = gramline

            else:
                del Dict[words]

        del Store[i]

    # end for (i in Store.keys())

    Store = {}

# end while (key in Grams)

print "and no variations found."
sys.stdout.flush()

# close corpus files

Corpus.close()
Constituents.close()
Grams.close()
