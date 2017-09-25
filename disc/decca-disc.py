#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)


""" decca-disc.py

Code to calculate all variation n-grams for corpora with discontinuous
constituents. Takes in a corpus (input_corpus) in line-by-line format, as
well as a text file of constituents augmented with NIL elements by
triefilter.py (filtertries), and writes out n files as described in   
Dickinson and Meurers (2005) "Detecting Errors in Discontinuous Structural
Annotation" (ACL-05).

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

input_corpus = "/home/user/research/decca/disc/corpus.txt"
cached_corpus = "/home/user/research/decca/disc/corpus.bsddb"
cached_boundaries = "/home/user/research/decca/disc/corpus.cb.bsddb"
filtertries = "/home/user/research/decca/disc/filtertries.txt"

destination_dir = "/home/user/research/decca/disc/output"
output_file_stem = "corpus-unit"

# unit is the window we are examining -- i.e. the length of the string
# covered by a nonterminal

unit = 2

# use plaintext output: 0, xhtml: 1

xhtml = 1

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
arglist = ['unit=','corpus=','cached-corp=','cached-bound=','directory=','ftree=','file=','xhtml','help'] 
# parse the command line call
opts, args = getopt.getopt(sys.argv[1:],"u:c:b:a:t:d:f:x:h",arglist)

# Go through the command line options and see if the user specified a
# directory or a corpus, or asked for help

for option, specification in opts:
    if option in ("-u", "--unit"):
        strunit = specification
        unit = int(strunit)
    elif option in ("-d", "--directory"):
        destination_dir = specification
    elif option in ("-c", "--corpus"):
        input_corpus = specification
    elif option in ("-b", "--cached-corp"):
        cached_corpus = specification;
    elif option in ("-a", "--cached-bound"):
        cached_boundaries = specification
    elif option in ("-t", "--ftree"):
        filtertries = specification
    elif option in ("-x", "--xhtml"):
        if xhtml == 0:
	  newxhtml = 1
	if xhtml == 1:
	  newxhtml = 0
	xhtml = newxhtml
    elif option in ("-f", "--file"):
        file_name = specification
    elif option in ("-h", "--help"):
        print """

Code to calculate all variation n-grams for corpora with discontinuous
constituents. Takes in a corpus (input_corpus) in line-by-line format, as
well as a text file of constituents augmented with NIL elements by
triefilter.py (filtertries), and writes out n files as described in   
Dickinson and Meurers (2005) "Detecting Errors in Discontinuous Structural
Annotation" (ACL-05).

Options:

-u/--unit          specify the unit length
-c/--corpus        specify the (absolute) corpus file name
-b/--cached-corp   specify the (absolute) cached corpus file name
-a/--cached-bound  specify the (absolute) cached boundaries file name
-t/--ftree         specify the (absolute) filter tries file name
-d/--directory     specify the (absolute) output directory name
-f/--file          specify the base name for the output files
-x/--xhtml         toggle XHTML output
-h/--help          display this help menu
"""
               
        sys.exit()

# create output string for unit setting
if unit < 10:
    unit_str = "00" + str(unit)
elif unit < 100:
    unit_str = "0" + str(unit)
else:
    unit_str = str(unit)

# print output settings
if xhtml:
    print "Generating XHTML output."
else:
    print "Generating plain text output."


# add a trailing "/" if not already there since it's a directory
if destination_dir[len(destination_dir)-1] != "/":
    destination_dir += "/"

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

# FUNCTIONS WHICH MANIPULATE BINARY VALUES

# -----

def get_small_binary(binary):

    """ takes in a 'binary' representation of the coverage of an
    n-gram within the corpus and returns a binary representation
    representing the coverage of the nucleus within the n-gram """
    
    small = ""
    for i in range(len(binary)):
        # add '1' to the returning value if we see '1' in the input
        if binary[i] == "1":
            small += "1"
        # convert 'X' (=seen but not in the nucleus) into '0'
        elif binary[i] == "X":
            small += "0"
    return small

# -----

def get_new_binaries(binary):

    """ take a binary number and find which middle values need to be
    filled, and return a list of triples: the offset within the corpus
    (word_offset), the offset within the n-gram (n_offset), and the
    new binary value """

    # initialize the list to hold all binary triples
    bin_list = []
    for i in range(len(binary)):
        # '0' is the indicator that the value needs to be filled in
        if binary[i] == "0":
            # only expand if there is something already in the ngram
            # next to it - i.e. we are on the "edge" of the element
            # (one of the surrounding elements has to be non-zero)
            
            if binary[i-1] != "0" or binary[i+1] != "0":
                # len(binary)-i-1 gives us the offset from the original
                # corpus position (because we count from right to left)
                #word_offset = len(binary)-i-1
		word_offset = i

                # call get_new_binary, which will give us a new binary
                # number, as well as tell us the offset of the nucleus
                # within the n-gram
                new_binary, n_offset = get_new_binary(binary,i)
                # add the triple to the list
                bin_list.append((word_offset,n_offset,new_binary))
    # return the list
    return bin_list

# -----

def get_new_binary(binary,pos):

    """ get_new_binary takes a binary value and a position (pos) where
    previously there was a '0' and calculates a new binary value.
    Additionally, it calculates the position of the word to be
    inserted within the n-gram (nbinary_counter) """
    
    # initialize the variables
    new_binary = ""
    nbinary_counter = 0
    seen = 0
    for i in range(len(binary)):

        # pos is the spot where the value is to be added; indicate
        # this change by adding an X to new_binary
        if i == pos:
            new_binary += "X"

        elif i < pos and binary[i] != "0":
            nbinary_counter += 1
            new_binary += binary[i]

        # new_binary simply copies binary except in the case where it
        # was the indicated spot
        else:
            new_binary += binary[i]
    # return the new binary value, as well as the nucleus offset
    return new_binary, nbinary_counter

# --------------------------------------------------------

# useful functions which prevent repeated coding

def get_oneline_info(oneline):

    # the pertinent information is separated by a double colon
    # (anything which does not appear in the corpus would suffice)
    newspl = oneline.split(tokensep)

    # get the cat, binary, nbinary, and words information
    cat = newspl[0]
    binary = newspl[1]
    nbinary = newspl[2]
    words = tokensep.join(newspl[3:])

    return cat,binary,nbinary,words

def get_corpus_word(corppos):
    corpline = Corpus[corppos]
    corpspl = corpline.split('\t')
    this_word = corpspl.pop()

    return this_word

def get_sent_num(sentindex):
    sarray = sentindex.split('_')

    return sarray[0][1:]

def get_nucleus(words,nbinary):
    wordlist = words.split(tokensep)
    nuc_list = []
    for i in range(len(nbinary)):
        if nbinary[i] == '1':
            word = wordlist[i]
            nuc_list.append(word)
    return " ".join(nuc_list)

def increment(D,words,nucleus,cat,binary):
    if D[words][nucleus].has_key(cat):
        if D[words][nucleus][cat].has_key(binary):
            D[words][nucleus][cat][binary] += 1
        else:
            D[words][nucleus][cat][binary] = 1
    else:
        D[words][nucleus][cat] = {binary:1}

def add_to_d(D,words,nbinary,binary,cat):

    nucleus = get_nucleus(words,nbinary)

    # add the words and nbinary values to D
    if D.has_key(words):
        if D[words].has_key(nucleus):
            increment(D,words,nucleus,cat,binary)
        else:
            D[words][nucleus] = {}
            increment(D,words,nucleus,cat,binary)
    else:
        D[words] = {}
        D[words][nucleus] = {}
        increment(D,words,nucleus,cat,binary)

def line_compare(a, b):
    aparts = a.split("\t")
    bparts = b.split("\t")
    return int(bparts[0]) - int(aparts[0])

def get_n_str(n):
    # define n_str as str(n) padded with leading 0s, for
    # output/filenames.
    if (n < 10):
        n_str='00'+str(n)
    elif (n+unit-1 < 100):
        n_str='0'+str(n)
    else:
        n_str=str(n)

    return n_str

def print_output(Output, filename):
    if os.path.exists(filename):
        sys.stderr.write("\n\nError: Output file " + filename + " already exists.\n")
        sys.exit(1)

    try:
        file = open(filename,'w')
    except:
        sys.stderr.write("\n\nError: Unable to open file " + filename + "\n")
        sys.exit(1)

    if xhtml:
        # set up html header and beginning of dl for output
        file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        file.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n')
        file.write("<head><title>" + os.path.basename(filename) + "</title>\n")
        file.write('<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=' + charencoding + '" />\n')
        file.write('<meta http-equiv="content-language" content="en" />\n')
        file.write("</head>\n<body>\n")

    for line in Output:
        file.write(line + "\n")

    if xhtml:
        file.write("</body>\n</html>\n")

    file.close()

def gen_output(D, Dpositions):
    # --------
    # VERIFICATION
    # check to see if there are variations before opening output file
    variations = 0
    words = D.keys()

    # loop only until 1 variation is found
    while len(words) > 0 and variations == 0:
        wordskey = words.pop()
        for nbinaries in D[wordskey].keys():
            if len(D[wordskey][nbinaries])>1:
	        variations = 1
		break

    # if no variations are found, return 0
    if variations == 0:
        return 0

    # -----------------
    # GENERATING OUTPUT
    # generate lines for all the n-grams in D, which will be the varying ones

    Output = []

    # loop through D
    for words in D.keys():
        # initialize the line and total counts
        line = words
        total = 0

        # nb: the total should be the same for all nbinaries
        for nbinaries in D[words].keys():
            if len(D[words][nbinaries])>1:
	        if xhtml:
		    wordlist = words.split(tokensep)
		    line = "<b>" + " ".join(wordlist) + "</b> ( " + nbinaries + " )"

		    line += "</dt><dd>"
		    line += "<ul>"

		    currentlines = []

	        else:
                    line = words + '\t' + ' (' + str(nbinaries) + ') -- '
            
                # for all cats (the actual variation), print them out
                # with their counts
                for cat in D[words][nbinaries]: ##.samples():
                    this_count = 0
                    for binaries in D[words][nbinaries][cat]:
                        count = D[words][nbinaries][cat][binaries]
                        this_count += count

		    if xhtml:
		        templine = ""
		        poskey = words + tokensep + nbinaries + tokensep + binaries + tokensep + cat
			index = Dpositions[poskey]
			for inst in range(count):
			    position = int(index[inst])
			    sentid = SentIDIndex[position]
			    context = sentid + ": "

			    for i in range(int(index[inst]), int(index[inst]) + len(binaries)):
			        reli = i - int(index[inst])
				if binaries[reli] == "0":
				    context += Corpus[str(i)] + " "
				elif binaries[reli] == "X":
				    context += '<font color="green">' + Corpus[str(i)] + "</font> "
				else:
				    context += '<font color="green"><u>' + Corpus[str(i)] + "</u></font> "
			    templine += "<li>" + context + "</li>\n"
				
			currentlines.append("<li>" + str(this_count) + ":" + cat + " <ul>" + templine + "</ul></li>")

	            else:
                        line = line + '  ' + str(this_count) + ':' + cat
                        line = line + ' [' + str(D[words][nbinaries][cat]) + '] '
                    total += this_count

            # delete this subentry
            del D[words][nbinaries]

        # finish the line and print it to the file
        if total:
	    if(xhtml):
                line = str(total) + "\t" + line + " ".join(currentlines)
		line += "</ul>"
		Output.append(line)
	    else:
                line = str(total) + "\t" + line
	        Output.append(line)
            ##file.write(line+'\n')
        
        # delete this entry
        del D[words]

    ##file.close()

    Output.sort(line_compare)

    if xhtml:
	for i in range(0, len(Output)):
	  Output[i] = "<dl><dt>" + str(i+1) + ". " + Output[i] + "</dd></dl>\n"
	  i += 1

    # return 1 since variations were found
    return [1, Output]

# --------------------------------------------------------

# FUNCTION TO CALCULATE NEW N-GRAMS

def get_new_ngram(words,cat,binary,nbinary,start):

    """ Take (n-1)gram information and get information for all
    potential new n-grams (new positions, new words, new binaries,
    etc. """

    # initialize list which will be returned
    to_return = []
    # get the words into list form (to easier insert new words)
    wordlist = words.split(tokensep)

    # ---------
    # Left Side

    # make sure that moving one position to the left is still within
    # the corpus
    if int(start) > 1 and (not Boundaries.has_key(str(start))):

        # get the position of the word to be added and eventually
        # insert the word into the wordlist
        corppos = str(int(start) - 1)
        this_word = get_corpus_word(corppos)
        wordlist.insert(0,this_word)

        # get the values for all relevant information, based on the
        # fact that we have added one word to the left
        this_words = tokensep.join(wordlist)
        this_binary = "X" + binary
        this_nbinary = "0" + nbinary
        this_start = str(int(start) - 1)

        # put all the info together and append it to the to_return list
        this_quint = (this_words,cat,this_binary,this_nbinary,this_start)
        to_return.append(this_quint)

        # be sure to remove the added word, since we will add others
        # in new locations (to the right and the middle)
        wordlist.pop(0)

    # ----------
    # Right Side

    # make sure that adding a word to the right will not exceed the
    # corpus
    if (int(start)+len(binary)) < corplength and (not Boundaries.has_key(str(int(start)+len(binary)))):

        # get the position of the word to be added and eventually
        # insert the word into the wordlist
        corppos = str(int(start)+len(binary))
        this_word = get_corpus_word(corppos)
        wordlist.append(this_word)

        # get the values for all relevant information, based on the
        # fact that we have added one word to the right
        this_words = tokensep.join(wordlist)
        this_binary = binary + "X"
        this_nbinary = nbinary + "0"
        this_start = start

        # put all the info together and append it to the to_return list
        this_quint = (this_words,cat,this_binary,this_nbinary,this_start)
        to_return.append(this_quint)

        # be sure to remove the added word, since we will add others
        # in new locations (in the middle)
        wordlist.pop()

    # -------------
    # Middle "side"

    # first, get a list of different positions to add information to
    binary_list = get_new_binaries(binary)
    if binary_list:
        for (offset,n_offset,this_binary) in binary_list:

            # get the position of the word to be added and get the
            # word itself
            corppos = str(int(start)+offset)
            this_word = get_corpus_word(corppos)

            # n_offset tells us where the new word goes within the
            # n-gram (i.e. irrespective of how many gaps there still
            # are in the corpus), so we insert this_word at position
            # n_offset
            wordlist.insert(n_offset,this_word)

            # get the values for all relevant information, based on the
            # fact that we have added one word in the middle
            this_words = tokensep.join(wordlist)
            this_nbinary = get_small_binary(this_binary)
            this_start = start

            # put all the info together and append it to the to_return list
            this_quint = (this_words,cat,this_binary,this_nbinary,this_start)
            to_return.append(this_quint)

            # be sure to remove the added word, since we might add others
            # in new locations in the middle
            wordlist.pop(n_offset)

    # return the list
    return to_return

# --------------------------------------------------------

# we are working with the base case "unit-grams", so we set n to be 1
# (they can be thought of as essentially unigrams)
n = 1

print "Working with window units of length " + str(unit)

print "Using corpus: "+input_corpus
print "Writing to:   "+destination_dir
sys.stdout.flush()

# --------------------------------------------------------
# STEP 1:  Read in corpus, finding sentence boundaries if needed
# If either the cached corpus or cached boundaries file does not exist, start
# from scratch reading in the input_corpus

# set the corpus counter to be 1, the start of the corpus
i = 1

# read in the corpus, word by word with no annotation and keep track of 
# sentence boundaries
if not os.path.exists(cached_corpus) or not os.path.exists(cached_boundaries):
    try:
        corpus_file = open(input_corpus,'r')
    except:
        sys.stderr.write("\n\nError: Unable to open corpus file " + input_corpus + "\n")
        sys.exit(1)

    try:
        TempCorpus = bsddb.btopen(cached_corpus, 'n')
    except:
        sys.stderr.write("\n\nError: Unable to open cached_corpus file for writing\n" + cached_corpus + "\n")
	sys.exit(1)

    try:
        Boundaries = bsddb.btopen(cached_boundaries, 'n')
    except:
        sys.stderr.write("\n\nError: Unable to open cached_boundaries file for writing\n" + cached_boundaries + "\n")
	sys.exit(1)

    prev_sentindex = ""

    line = corpus_file.readline()
    while line:
        # get the word at each position
        line = line.strip()
        if line:
            spl = line.split('\t')

            # add the word to the Corpus dictionary
            word = spl[1]
	    # extract sNN from corpus id sNN_NN
	    pos = spl[0].split("_")[0]
            TempCorpus[str(i)] = pos + "\t" + word

	    # find sentence boundaries and store in Boundaries
	    sentindex = get_sent_num(spl[0])
	    if sentindex != prev_sentindex:
	        prev_sentindex = sentindex
	        Boundaries[str(i)] = "1"
    
            # iterate i and get the next line
            i = i + 1
        line = corpus_file.readline()

    corpus_file.close()
    print "Corpus read in and cached."
    sys.stdout.flush()
else:
    TempCorpus = bsddb.btopen(cached_corpus)
    Boundaries = bsddb.btopen(cached_boundaries)
    print "Cached corpus read in."
    sys.stdout.flush()

# index of sentence IDs for each corpus position
SentIDIndex = {}

# corpus
Corpus = bsddb.btopen(None)

for key, line in TempCorpus.iteritems():
  lineparts = line.split("\t")
  SentIDIndex[int(key)] = lineparts[0]
  Corpus[key] = lineparts[1]

TempCorpus.close()

# set corplength to be the length of the corpus (plus 1)
corplength = len(Corpus.keys()) + 1

# --------------------------------------------------------
# STEP 2: Read in nonterminals and filtertries which match non-terminals
# and process base case where n = unit length

# tell the user we're starting to work on this n
n_str = get_n_str(n+unit-1)
print n_str+" grams:",
sys.stdout.flush()

# create D, the dictionary of variations
D = {}

# create Dpositions to keep track of where each variation appeared in the
# corpus
Dpositions = {}

# set Grams to be an empty dictionary
Grams = bsddb.btopen(None)

# open up the file which contains all the nonterminal stretches of
# text and stretches of text which are string-identical

try:
    nonterminals = open(filtertries,'r')
except:
    sys.stderr.write("\n\nError: Unable to open filtertries file \n" + filtertries + "\n")

line = nonterminals.readline()

# loop until there are no more nonterminal lines

while line:
    line = line.strip()
    spl = line.split('\t')

    # we only want to deal with windows of unit length (unit+3 because
    # of the index, cat, and binary labels)
    if (len(spl) == unit + 3):
        # get the index, cat, and binary labels from the line
        index = spl.pop(0)
        cat = spl.pop(0)
        binary = spl.pop(0)
        # nbinary is the coverage of the nucleus within the n-gram
        nbinary = get_small_binary(binary)

        # the remaining part of the line/spl is the words of the
        # nonterminal
        span = tokensep.join(spl)

        # Grams will be in the form:
        # cat1::binary1::nbinary1::span1 \n ... catN::binaryN::nbinaryN::spanN

        # for the base case, all nbinary value for the unigrams are
        # composed of 1's and are equal to the length of the current
        # unit

        # add this information to Grams: either by creating a new
        # entry for this index, or by adding a new line of information
        if Grams.has_key(index):
            Grams[index] += "\n" + cat + tokensep + binary + tokensep + nbinary + tokensep + span
        else:
            Grams[index] = cat + tokensep + binary + tokensep + nbinary + tokensep + span

    # read the next line
    line = nonterminals.readline()

# we now loop over Grams to store the n-grams in a dictionary (D),
# which will be used to keep track of varying n-grams

for index, line in Grams.iteritems():

    # get information from Grams and break it down line-by-line (each
    # line corresponds to a new n-gram at that index
    spl = line.split('\n')

    # loop through the different n-grams (here: oneline)
    for oneline in spl:

        # get all relevant info from this line
        cat,binary,nbinary,words = get_oneline_info(oneline)

        # D will be in the form:
        # D[words] = {offset:<FreqDist of cats>, ...}

        # increment the cat value for the words and for this nbinary
        # [note that in the base case all nbinary values are
        # identical since every word in the n-gram is in the nucleus]

        # add info to dictionary
        add_to_d(D,words,nbinary,binary,cat)

        # keep track of corpus position for this line
	poskey = words + tokensep + get_nucleus(words, nbinary) + tokensep + binary + tokensep + cat
        if Dpositions.has_key(poskey):
	    Dpositions[poskey].append(index)
	else:
	    Dpositions[poskey] = [index]
        
# print a note that the nonterminals have been read in
print "nonterminals read in,",
sys.stdout.flush()

# --------------------------------------------------------

# filter out the nonvariations in Grams

# get the first key and cycle through all the keys in Grams
for key in Grams.keys():
    line = Grams[key]

    # get the information for all n-grams which start at this
    # key/index
    spl = line.split('\n')

    # new will hold all the n-grams which have variation
    new = []
    # loop through all the n-grams/onelines at this position
    for oneline in spl:

        # get all relevant info from this line
        cat,binary,nbinary,words = get_oneline_info(oneline)

        nucleus = get_nucleus(words,nbinary)

        # if there is variation (samples>1), add this n-gram to new
        if D.has_key(words) and len(D[words][nucleus]) > 1:
            new.append(oneline)

    # if there was at least one n-gram which varied, new will be
    # non-empty, so add it back to Grams
    if new:
        newline = "\n".join(new)
        Grams[key] = newline
    # if there was no variation, it should be removed from Grams
    else:
        del Grams[key]

# --------------------------------------------------------
# STEP 3: loop over increasing longer n-grams until none found

# NOW BEGINS THE (non-base case) A PRIORI WORK

# Grams[i] = cat1 ## binary1 ## nbinary1 ## words1 \n ... \n catN ## binaryN ## nbinaryN ## wordsN

# D[words] = {nbinary1:<FreqDist>, ..., nbinaryN:<FreqDist>} [nbinary
# = nucleus binary]

# MAIN LOOP: loop until Grams, which stores all varyingly-tagged
# n-grams, has no more elements -- i.e. there are not n-grams of that
# size which are tagged in multiple ways [There may be entries in Grams 
# but no actual variations. If this is the case, print_d will return 0
# and the file will not be created.]

variations_found = 1

while Grams and variations_found:
    # prepare to print to file
    filename = destination_dir+n_str

    (variations_found, Output) = gen_output(D, Dpositions)

    # if there were indeed variations, tell the user and
    # proceed with n-gram n+1
    # (otherwise, the rest of loop is skipped and it exits)
    if variations_found:
        # print a message that the variations have been found
        print "variations found,",
        sys.stdout.flush()

	if xhtml:
	  filename = filename + ".html"

	print_output(Output, filename)

        # print out a note to the screen that these n-grams are finished.
        print "written to file,",
        sys.stdout.flush()

        # sort the file using unix sort, output into the file itself
        ##commands.getstatusoutput("sort -nr "+filename+" -o "+filename)

        print "and file sorted."

        sys.stdout.flush()

        # Increment n: we are now dealing with the next higher n-gram
        n = n + 1

        # (re)initialize Store, which will store the n-grams, indexed by the
        # corpus position of the first element in the n-gram
        Store = bsddb.btopen(None)

        # (re)initialize D, which will for each n-gram corpus position
        # store the tag sequence that occurs for any occurrence of this
        # n-gram
        D = {}

	# (re)initialize Dpositions
	Dpositions = {}

        n_str = get_n_str(n+unit-1)
        # tell user we're starting work on this n:
        print n_str+" grams:",
        sys.stdout.flush()

        # Grams holds all the n-1 grams in string form, so we cycle through them.
        for key, line in Grams.iteritems():

            spl = line.split('\n')

            # loop through the different n-grams (here: oneline)
            for oneline in spl:

                # get all relevant info from this line
                cat,binary,nbinary,words = get_oneline_info(oneline)

                # somelist will hold all the potential new n-grams: their
                # words, cat label (same), binary value, n(ucleus)binary
                # value, and start position
                somelist = get_new_ngram(words,cat,binary,nbinary,key)

                # loop through all potential new n-grams
                for item in somelist:
                    # get their relevant information
                    (words,cat,binary,nbinary,start) = item

                    # check to see if we have already added something to
                    # Store for this position
                    if Store.has_key(start):
                        newline = Store[start]
                        newspl = newline.split('\n')

                        # cycle through the different lines in newspl to
                        # see if any match the current item
                        seen = 0
                        for twoline in newspl:

                            # get all relevant info from this line
                            twocat,twobinary,twonbinary,twowords = get_oneline_info(twoline)

                            # use binary to test for identity
                            if binary == twobinary:
                                # we're recalcuating the same thing, so
                                # ignore it
                                seen = 1

                        # if seen=0, this line is new for this particular
                        # start index in Store, so tack it on to the Store
                        # value
                        if not seen:

                            # add the new information to Store, as part of
                            # the data for this corpus position
                            to_add = newline + "\n"
                            to_add += cat + tokensep + binary + tokensep + nbinary + tokensep + words
                            Store[start] = to_add

                            # add info to dictionary
                            add_to_d(D,words,nbinary,binary,cat)

			    # keep track of corpus position for this line
			    poskey = words + tokensep + get_nucleus(words, nbinary) + tokensep + binary + tokensep + cat
                            if Dpositions.has_key(poskey):
			        Dpositions[poskey].append(start)
		            else:
			        Dpositions[poskey] = [start]

                        # if seen=1, then we've already dealt with this
                        # line, so there is nothing new to do, just put
                        # newline back into Store
                        else:
                            Store[start] = newline
                            
                    # not Store.has_key(start), i.e. Store does not have
                    # anything starting at this line
                    else:
                        # so, add a line to Store here
                        Store[start] = cat + tokensep + binary + tokensep + nbinary + tokensep + words

                        # add info to dictionary
                        add_to_d(D,words,nbinary,binary,cat)

			# keep track of corpus position for this line
			poskey = words + tokensep + get_nucleus(words, nbinary) + tokensep + binary + tokensep + cat
                        if Dpositions.has_key(poskey):
			    Dpositions[poskey].append(start)
		        else:
			    Dpositions[poskey] = [start]

            # get the next key value
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
            spl = storeline.split('\n')

            # set gramline to the empty string
            gramline = ""

            # loop through the different n-grams (here: oneline)
            for oneline in spl:

                # get all relevant info from this line
                cat,binary,nbinary,words = get_oneline_info(oneline)

                # if 'words' is a varying n-gram, put it in Grams.
                # Otherwise, get rid of it from D

                nucleus = get_nucleus(words,nbinary)
            
                if D.has_key(words):
                    # set variation to 0; we will see if any of the nbinaries
                    # are varying.  If so, we keep it (otherwise, delete
                    # nbinaries that result in no variation)
                    variation = 0

                    # loop through all nbinaries, in order to detect if
                    # there is variation
                    for nbinaries in D[words].keys():
                        if len(D[words][nbinaries]) > 1:

                            # add to the gramline iff this nbinary results
                            # in variation
                            if nucleus == nbinaries:
                                if gramline:
                                    gramline += '\n' + oneline
                                else:
                                    gramline = oneline
                                
                            # indicate that we have found some variation
                            # within D[words]
                            variation = 1

                        # not variation
                        else:
                            del D[words][nbinaries]

                    # remove the value of D[words] if there was no variation
                    if not variation:
                        del D[words]

            # gramline is only non-empty if variation was found for this
            # corpus position, so add it back to Grams
            if gramline:
                Grams[i] = gramline

            # empty Store out
            del Store[i]

        # end for (i in Store.keys())

        Store.close()
        Store = bsddb.btopen(None)

    # end if variations_found

# end while (key in Grams)

print "and no variations found."
sys.stdout.flush()

# close Grams
Grams.close()
Corpus.close()
