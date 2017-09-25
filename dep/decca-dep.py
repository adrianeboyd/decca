#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2009 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)


""" decca-dep.py

Code to calculate all variation n-grams for dependency corpora.

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

# Algorithm settings

usedeppos = 0                 # use dependent POS instead of word 
                              # in comparisons
filter_punctuation = 0        # see filter on line 937; the example
                              # uses PDT punctuation tag filter,
			      # customize for your corpus if you set 
			      # this to 1

# Output settings

charencoding = "utf-8"        # encoding for xhtml output

# See line 567 to choose the appropriate context filter for your corpus.
# See Boyd et al. 2008 section 4.2 for explanations of each heuristic.

# Optional: default parameters to be used if unspecified on command line
# (Files specified on command line will override these settings.)

input_corpus = "/path/to/corpus.conll"
filtertries = "/path/to/filtertries.txt"
destination_dir = "/path/to/output/dir"
output_file_stem = "dep"

# --------------------------------------------------------
# END USER SETTINGS
# --------------------------------------------------------

# import included modules
import getopt
import sys
import os
import re
import commands

# import extra modules
import bsddb
from nltk_freqdist import *

# specify the long options in arglist
arglist = ['corpus=','ftree=','file=','xhtml','help']
# parse the command line call
try:
    opts, args = getopt.getopt(sys.argv[1:],"d:c:t:f:x:h",arglist)
except:
    sys.stderr.write("\nInvalid commandline argument(s).")
    opts = [["-h", "-"]]

# Go through the command line options and see if the user specified a
# directory or a corpus, or asked for help

for option, specification in opts:
    if option in ("-d", "--directory"):
        destination_dir = specification
    elif option in ("-c", "--corpus"):
        input_corpus = specification
    elif option in ("-t", "--ftree"):
        filtertries = specification
    elif option in ("-f", "--file"):
        output_file_stem = specification
    elif option in ("-p", "--deppos"):
        usedeppos = 1
    elif option in ("-x", "--xhtml"):
        xhtml = 1
    elif option in ("-h", "--help"):
        print """

Code to calculate all variation n-grams for dependency corpora.

Options:

-c/--corpus        specify the (absolute) corpus file name
-t/--ftree         specify the (absolute) filter tries file name
-d/--directory     specify the (absolute) output directory name
-f/--file          specify the base name for the output files
-p/--deppos        use part-of-speech for dependent word
-x/--xhtml         produce filtered xhtml output
-h/--help          display this help menu
"""
        sys.exit()

# add a trailing "/" if not already there since it's a directory
if destination_dir[len(destination_dir)-1] != "/":
    destination_dir += "/"
# create output directory if it doesn't exist
if not os.path.exists(destination_dir):
    print commands.getoutput("mkdir " + destination_dir)
    print "Creating directory " + destination_dir

# there is support in the code for text output, but it has not 
# been tested for quite some time, so set xhtml to 0 at your own risk

xhtml = 0

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
    for i in range(len(binary)):

        # pos is the spot where the value is to be added; indicate
        # this change by adding an X to new_binary
        if i == pos:
            new_binary += "X"

        # if we have seen our filled-in spot and encounter an 'X' or a
        # '1' (i.e. not a '0'), this means that there is another value
        # to count in the offset
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

def get_sent_num(id):
    sarray = id.split('_')

    return int(sarray[0][1:])

def get_word_num(id):
    sarray = id.split('_')

    return int(sarray[1])

def id_modify(id, offset):
    word_num = get_word_num(id)
    word_num += offset

    return id.split('_')[0] + "_" + str(word_num)

def increment(D,words,nbinary,cat,binary):
    if D[words][nbinary].has_key(cat):
        if D[words][nbinary][cat].has_key(binary):
            D[words][nbinary][cat][binary] += 1
        else:
            D[words][nbinary][cat][binary] = 1
    else:
        D[words][nbinary][cat] = {binary:1}

def add_to_d(D,words,nbinary,binary,cat):

    # add the words and nbinary values to D
    if D.has_key(words):
        if D[words].has_key(nbinary):
            increment(D,words,nbinary,cat,binary)
        else:
            D[words][nbinary] = {}
            increment(D,words,nbinary,cat,binary)
    else:
        D[words] = {}
        D[words][nbinary] = {}
        increment(D,words,nbinary,cat,binary)

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

def line_compare(a, b):
    aparts = a.split("\t")
    bparts = b.split("\t")
    return int(bparts[0]) - int(aparts[0])

def nilfilter(binary, position):
    ones = {}
    for i in range(len(binary)):
        if binary[i] == '1':
            ones[i] = 1

    if len(ones) == 1:
        onepos = ones[0]
        left = 0
        right = 0

        # check left side
        if onepos > 0:
	    if binary[onepos - 1] == 'X':
	        left = 1
	if onepos == 0 and position.split("_")[1] == "1":
	    left = 1

        # check right side
	if onepos < len(binary) - 1:
	    if binary[onepos + 1] == 'X':
	        right = 1

        right_position = id_modify(position, len(binary) - 1)
	if onepos == len(binary) - 1 and Boundaries.has_key(right_position):
	    right = 1

        if left == 1 and right == 1:
            return 1

    else:
        onekeys = ones.keys()
        onekeys.sort()

        onepos1 = onekeys[0]
        onepos2 = onekeys[1]
        for i in range(onepos1 + 1, onepos2):
            if binary[i] == '0':
                return 0

        # else, good
        return 1


def nonfringe(binary, position):
    ones = {}
    for i in range(len(binary)):
        if binary[i] == '1':
	    ones[i] = 1

    for onepos in ones.keys():
        left = 0
	right = 0

        # check left side
        if onepos > 0:
	    if binary[onepos - 1] == '1' or binary[onepos - 1] == 'X':
	        left = 1
	if onepos == 0 and position.split("_")[1] == "1":
	    left = 1

        # check right side
	if onepos < len(binary) - 1:
	    if binary[onepos + 1] == '1' or binary[onepos + 1] == 'X':
	        right = 1

	right_position = id_modify(position, len(binary) - 1)
	if onepos == len(binary) - 1 and Boundaries.has_key(right_position):
	    right = 1

        # this 1 isn't good, so is fringe
	if left == 0 or right == 0:
	    return 0

    # all 1's check out, so is not fringe
    return 1

def countall(hash):
    count = 0
    for key,group in hash.iteritems():
        count += len(group)

    return count

def print_d(D,filename):
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

    if os.path.exists(filename):
        sys.stderr.write("\n\nError: Output file " + filename + " already exists.\n")
        sys.exit(1)

    try:
        file = open(filename,'w')
    except:
        sys.stderr.write("\n\nError: Unable to open file " + filename + "\n")
        sys.exit(1)

    # --------
    # PRINTING
    # print out all the n-grams in D, which will be the varying ones

    # loop through D
    for words in D.keys():

        # initialize the line and total counts
        line = words
        total = 0

        # nb: the total should be the same for all nbinaries
        for nbinaries in D[words].keys():

            if len(D[words][nbinaries])>1:
                line = line + '\t' + ' (' + str(nbinaries) + ') -- '

                # for all cats (the actual variation), print them out
                # with their counts
                for cat in D[words][nbinaries]:
                    this_count = 0
                    for binaries in D[words][nbinaries][cat]:
                        count = D[words][nbinaries][cat][binaries]
                        this_count += count
                    line = line + '  ' + str(this_count) + ':' + cat
                    line = line + ' [' + str(D[words][nbinaries][cat]) + '] '
                    total += this_count

            # delete this subentry
            del D[words][nbinaries]

        # finish the line and print it to the file
        if total:
            line = str(total) + "\t" + line
            file.write(line+'\n')

        # delete this entry
        del D[words]

    file.close()
    return 1

def maxlen(hash):
    max = 0
    for ekey, egroup in hash.iteritems():
        ekeyparts = ekey.split(tokensep)
        n = int(ekeyparts[0])
        if n > max:
            max = n

    return max



def print_xhtml_output(filename,output):
    filename += "html"

    if os.path.exists(filename):
        sys.stderr.write("\n\nError: Output file " + filename + " already exists.\n")
        sys.exit(1)

    try:
        file = open(filename,'w')
    except:
        sys.stderr.write("\n\nError: Unable to open file " + filename + "\n")
        sys.exit(1)

    # --------
    # PRINTING
    # print out all the n-grams in D, which will be the varying ones

    # set up html header and beginning of dl for output
    file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    file.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">\n')
    file.write("<head><title>" + os.path.basename(filename) + "</title>\n")
    file.write('<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=' + charencoding + '" />\n')
    file.write('<meta http-equiv="content-language" content="en" />\n')

    file.write("</head>\n<body>\n<ol>\n")

    longest = {}
    # pass through output to sort by longest n-gram length
    for key, group in output.iteritems():
        length = maxlen(group)
        if not longest.has_key(length):
            longest[length] = []
        longest[length].append(key)

    longestkeys = longest.keys()
    longestkeys.sort()
    longestkeys.reverse()

    ## counts = {}
    ## # preliminary pass through output to sort by count
    ## for key,group in output.iteritems():
        ## if not counts.has_key(countall(group)):
            ## counts[countall(group)] = []
        ## counts[countall(group)].append(key)
 
    ## countskeys = counts.keys()
    ## countskeys.sort()
    ## countskeys.reverse()

    # print output in reverse order by total count
    ##for countkey in countskeys:
    for lenkey in longestkeys:
        ## for key in counts[countkey]:
        for key in longest[lenkey]:
            file.write("<li>\n")
            keyparts = key.split(tokensep)
            keystring = " ".join(keyparts)
            file.write(keystring)
            file.write('<ol type="a">\n')
            ecounts = {}
            for ekey,egroup in output[key].iteritems():
                ekeyparts = ekey.split(tokensep)
                n = int(ekeyparts[0])
                if not ecounts.has_key(n):
                  ecounts[n] = []
                ecounts[n].append(ekey)

            ecountskeys = ecounts.keys()
            ecountskeys.sort()
            ecountskeys.reverse()

            for n in ecountskeys:
                for ekey in ecounts[n]:
                    ekeyparts = ekey.split(tokensep)
                    if len(output[key][ekey]) > 0:
                        file.write("<li>" + ekeyparts[0] + ": " + ekeyparts[1] + '\n<ol type="i">\n')
                        for fkey,context in output[key][ekey].iteritems():
                            fkeyparts = fkey.split(tokensep)
                            file.write("<li>" + fkeyparts[0] + " " + context + "</li>\n")
                        file.write("</ol>\n</li>\n")

            file.write("</ol></li>\n")

    file.write("</ol>\n</body>\n</html>\n")
    file.close()

def add_to_xhtml_output(D,Dpositions,output,n):
    # loop through D
    toadd = []
    for words in D.keys():

        # nb: the total should be the same for all nbinaries
        for nbinaries in D[words].keys():

            if len(D[words][nbinaries])>1:
                nonfringe_cats = {}
                nonfringe_pos = {}
                nonfringe_heads = {}
		rels = {}
                tempadd = []

                for cat in D[words][nbinaries]:
                    for binaries in D[words][nbinaries][cat]:
                        count = D[words][nbinaries][cat][binaries]
	                poskey = words + tokensep + nbinaries + tokensep + binaries + tokensep + cat
		        index = Dpositions[poskey]
			# build up xhtml context for all non-fringe cases
			for inst in range(count):

			    ## Context filters:
			    ## uncomment one of the following if statements to
			    ## filter NIL/nonfringe instances

                            ## NIL internal context heuristic for NIL, 
			    ## non-fringe for non-NIL
			    #if (nilfilter(binaries, index[inst]) and nonfringe(binaries, index[inst]) and cat[0:3] == "NIL") or (nonfringe(binaries, index[inst]) and cat[0:3] != "NIL"):

			    ## NIL internal context heuristic for NIL, 
			    ## all non-NIL
			    #if (nilfilter(binaries, index[inst]) and cat[0:3] == "NIL") or cat[0:3] != "NIL":

			    ## non-fringe heuristic for all
			    #if nonfringe(binaries, index[inst]):

			    ## all (no filtering)
			    if True:
                                # find the corpus position of the beginning of
                                # this sentence
                                sentbegin = id

                                # use the corpus position to link to the
                                # sentence image 
				sentimage = index[inst].split('_')[0] + ".png"
			        context = "<a href=\"images/" + sentimage + "\">" + index[inst].split('_')[0] + "</a>: "

                                headpos = get_word_num(index[inst])
                                headstart = headpos
                                deppos = headpos

                                onecount = 0
                                if cat[-1] == "L":
                                    while onecount < 1:
                                        if binaries[headpos-headstart] == "1":
                                            onecount += 1
                                        headpos += 1
                                        deppos += 1
                                    while onecount < 2:
                                        if binaries[deppos-headstart] == "1":
                                            onecount += 1
                                        deppos += 1
                                elif cat[-1] == "R":
                                    while onecount < 1:
                                        if binaries[deppos-headstart] == "1":
                                            onecount += 1
                                        headpos += 1
                                        deppos += 1
                                    while onecount < 2:
                                        if binaries[headpos-headstart] == "1":
                                            onecount += 1
                                        headpos += 1

                                headpos -= 1
                                deppos -= 1

				headpos = index[inst].split('_')[0] + "_" + str(headpos)
				deppos = index[inst].split('_')[0] + "_" + str(deppos)

                                if usedeppos:
                                    outputkey = Corpus[str(headpos)] + tokensep + CorpusPOS[str(deppos)]
                                else:
                                    outputkey = Corpus[str(headpos)] + tokensep + Corpus[str(deppos)]
                                elementkey = cat + tokensep + str(headpos) + tokensep + str(deppos)

                                headrel = CorpusRel[str(headpos)]
				rels[headrel] = 1

                                nonfringe_cats[cat] = 1
                                nonfringe_pos[headpos] = 1
                                if nonfringe_heads.has_key(cat):
                                    nonfringe_heads[cat].append(headpos)
                                else:  
                                    nonfringe_heads[cat] = [headpos]

                                ngram = ""

			        for i in range(len(binaries)):
			            if binaries[i] == "0":
			                context += CorpusWords[id_modify(index[inst], i)] + " "
			            elif binaries[i] == "X":
			                context += '<font color="blue">' + CorpusWords[id_modify(index[inst], i)] + "</font> "
			            else:
			                context += '<b><font color="blue">' + CorpusWords[id_modify(index[inst], i)] + "/" + CorpusPOS[id_modify(index[inst], i)] + "</font></b> "


                                    if binaries[i] == "X" or binaries[i] == "1":
                                        if usedeppos and i == deppos:
                                            ngram += CorpusPOS[id_modify(index[inst], i)] + " "
                                        else:
                                            ngram += CorpusWords[id_modify(index[inst], i)] + " "


                                tempadd.append([outputkey,elementkey,ngram,context])

                # check to make sure that duplicate sentences aren't causing
                # extra results
                identical = 1  
                nfhkeys = nonfringe_heads.keys()
                for i in range(0, len(nfhkeys)):
                    nonfringe_heads[nfhkeys[i]].sort()
                for i in range(0, len(nfhkeys) - 1):     
                    group1 = nonfringe_heads[nfhkeys[i]]  
                    group2 = nonfringe_heads[nfhkeys[i+1]]
                    if group1 != group2:
                        identical = 0

                if len(nonfringe_cats) > 1 and len(nonfringe_pos) > 1 and identical == 0:
                    for line in tempadd:
                        outputkey = line[0]
                        elementkey = line[1]
                        ngram = line[2]
                        outputline = line[3]
			if len(rels) == 1:
			  outputline = outputline.replace('color="blue"', 'color="red"')
			# create the entry if it doesn't exist
                        if not output.has_key(outputkey):
                            output[outputkey] = {}
                        ngramkey = str(n) + tokensep + ngram
                        if not output[outputkey].has_key(ngramkey):
                            output[outputkey][ngramkey] = {}
                        # remove any shorter ngrams for this position
                        for nkey in output[outputkey].keys():
                            for ekey in output[outputkey][nkey].keys():
                                if ekey == elementkey:
                                    del output[outputkey][nkey][ekey]
                        output[outputkey][ngramkey][elementkey] = outputline

            # delete this subentry
            del D[words][nbinaries]

        # delete this entry
        del D[words]

    return 1


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
    if get_word_num(start) > 1:

        # get the position of the word to be added and eventually
        # insert the word into the wordlist
        corppos = start.split('_')[0] + "_" + str(get_word_num(start) - 1)
        this_word = get_corpus_word(corppos)
        wordlist.insert(0,this_word)

        # get the values for all relevant information, based on the
        # fact that we have added one word to the left
        this_words = tokensep.join(wordlist)
        this_binary = "X" + binary
        this_nbinary = "0" + nbinary
        this_start = id_modify(start, -1)

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
    
    # new right position
    if Corpus.has_key(id_modify(start, len(binary))):

        # get the position of the word to be added and eventually
        # insert the word into the wordlist
        corppos = id_modify(start, len(binary))
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
	    middle_num = get_word_num(start) + offset
	    middle_position = start.split('_')[0] + '_' + str(middle_num)
            corppos = str(middle_position)
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
try:
    corpus_file = open(input_corpus,'r')
except:
    sys.stderr.write("\n\nError: Unable to open corpus file " + input_corpus + "\n")
    sys.exit(1)

Corpus = bsddb.btopen(None)
CorpusPOS = bsddb.btopen(None)
CorpusRel = bsddb.btopen(None)
CorpusWords = bsddb.btopen(None)
Boundaries = {}

# keep track of previous sentence boundary for all tokens
prevBoundary = 1

line = corpus_file.readline()
line = line.strip()
spl = line.split('\t')
previd = spl[0]
prevsentid = int(previd.split("_")[0][1:])

while line:
    # get the word at each position
    line = line.strip()
    spl = line.split('\t')

    # add the word to the Corpus dictionary
    id = spl[0]
    Corpus[id] = spl[1]
    CorpusPOS[id] = spl[2]
    CorpusRel[id] = spl[3]
    CorpusWords[id] = spl[4]

    sentid = int(id.split("_")[0][1:])
    if prevsentid != sentid:
        Boundaries[previd] = 1

    prevsentid = sentid
    previd = id

    line = corpus_file.readline()

corpus_file.close()
print "Corpus read in."
sys.stdout.flush()

# set corplength to be the length of the corpus (plus 1)
corplength = len(Corpus.keys()) + 1

topdestination_dir = destination_dir

output = {}

for unit in range(2, 3):
    print "\nWorking with window units of length " + str(unit)

    n = unit

    # concatenate the path name with the file name and a dot for the
    # extension, to be used for this iteration
    destination_dir = topdestination_dir + output_file_stem + "."

# --------------------------------------------------------
# STEP 2: Read in nonterminals and filtertries which match non-terminals
# and process base case where n = unit length

    # tell the user we're starting to work on this n
    n_str = get_n_str(unit)
    print n_str+" grams:",
    sys.stdout.flush()

    # create D, the dictionary of variations
    D = {}
    # create Dpositions to keep track of where each variation appeared in
    # the corpus
    Dpositions = {}

    # set Grams to be an empty dictionary
    Grams = bsddb.btopen(None)

    # open up the file which contains all the nonterminal stretches of
    # text and stretches of text which are string-identical

    try:
        nonterminals = open(filtertries,'r')
    except:
        sys.stderr.write("\n\nError: Unable to open filtertries file \n" + filtertries + "\n")
        sys.exit(1)

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

	    if filter_punctuation == 0 or (CorpusPOS[index][0] != "Z" and CorpusPOS[id_modify(index, len(binary)-1)][0] != "Z"):

                # the remaining part of the line/spl is the words of the
                # nonterminal

                # if the category is NIL, either element could be the head
                # so create the needed L/R category labels and spans
                if cat == "NIL":
                    spl2 = spl[:]
                    # convert appropriate elements to POS if needed
                    if usedeppos:
                        spl[0] = "POS-" + CorpusPOS[index]
                        spl2[1] = "POS-" + CorpusPOS[id_modify(index, len(binary)-1)]
                    else:
                        spl[0] = "DEP-" + Corpus[index]
                        spl2[1] = "DEP-" + Corpus[id_modify(index, len(binary)-1)]
                    cat1 = "NIL-R"
                    span2 = tokensep.join(spl2)
                    cat2 = "NIL-L"
                # otherwise create category label and convert to POS if needed
                elif cat[-1] == "L":
                    if usedeppos:
                        spl[1] = "POS-" + CorpusPOS[id_modify(index, len(binary)-1)]
                    else:
                        spl[1] = "DEP-" + Corpus[id_modify(index, len(binary)-1)]
                    cat1 = cat
                elif cat[-1] == "R":
                    if usedeppos:
                        spl[0] = "POS-" + CorpusPOS[index]
                    else:
                        spl[0] = "DEP-" + Corpus[index]
                    cat1 = cat

                span = tokensep.join(spl)

                # Grams will be in the form:
                # cat1::binary1::nbinary1::span1 \n ... catN::binaryN::nbinaryN::spanN

                # for the base case, all nbinary value for the unigrams are
                # composed of 1's and are equal to the length of the current
                # unit

                # add this information to Grams: either by creating a new
                # entry for this index, or by adding a new line of information
                if Grams.has_key(index):
                    Grams[index] += "\n" + cat1 + tokensep + binary + tokensep + nbinary + tokensep + span
                else:
                    Grams[index] = cat1 + tokensep + binary + tokensep + nbinary + tokensep + span

                # add second NIL entry
                if cat == "NIL":
                    Grams[index] += "\n" + cat2 + tokensep + binary + tokensep + nbinary + tokensep + span2

        # read the next line
        line = nonterminals.readline()

    # we now loop over Grams to store the n-grams in a dictionary (D),
    # which will be used to keep track of varying n-grams

    for key, line in Grams.iteritems():

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
	    poskey = words + tokensep + nbinary + tokensep + binary + tokensep + cat
	    if Dpositions.has_key(poskey):
	        Dpositions[poskey].append(key)
            else:
	        Dpositions[poskey] = [key];

    # print a note that the nonterminals have been read in
    print "nonterminals read in,",
    sys.stdout.flush()

    # --------------------------------------------------------

    # filter out the nonvariations in Grams

    # get the first key and cycle through all the keys in Grams
    gramskeys = Grams.keys()
    for key in gramskeys:
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

            # if there is variation (samples>1), add this n-gram to new
            if D.has_key(words) and len(D[words][nbinary]) > 1:
                new.append(oneline)

        # the next key has to be found before we delete this one
        oldkey = key

        # if there was at least one n-gram which varied, new will be
        # non-empty, so add it back to Grams
        if new:
            newline = "\n".join(new)
            Grams[oldkey] = newline
        # if there was no variation, it should be removed from Grams
        else:
            del Grams[oldkey]

# --------------------------------------------------------
# STEP 3: loop over increasing longer n-grams until none found

# --------------------------------------------------------
# NOW BEGINS THE (non-base case) A PRIORI WORK

# Grams[i] = cat1::binary1::nbinary1::words1 \n ... \n catN::binaryN::nbinaryN::wordsN

# D[words] = {nbinary1:<FreqDist>, ..., nbinaryN:<FreqDist>} [nbinary
# = nucleus binary]

# MAIN LOOP: loop until Grams, which stores all varyingly-tagged
# n-grams, has no more elements -- i.e. there are not n-grams of that
# size which are tagged in multiple ways

    variations_found = 1

    while Grams and variations_found:
        # add results to hash

        if xhtml:
	    variations_found = add_to_xhtml_output(D,Dpositions,output,n)
	elif not xhtml:
            filename = destination_dir+n_str
            variations_found = print_d(D,filename)

        # if there were indeed variations, tell the user and
        # proceed with n-gram n+1
        # (otherwise, the rest of loop is skipped and it exits)
        if variations_found:
            # print a message that the variations have been found
            print "variations found,",
            sys.stdout.flush()

	    if not xhtml:
                # print out a note to the screen that these n-grams are finished.
                print "written to file,",

                # sort the text file output using unix sort, 
	        # output into the file itself
                commands.getstatusoutput("sort -nr "+filename+" -o "+filename)
                print "and file sorted."
	    else:
	        print "and written to file."

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
	    Dpositions = {}

            n_str = get_n_str(n)
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

                                # use binary and direction to test for identity
                                if binary == twobinary and cat[-1] == twocat[-1]:
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
	                        poskey = words + tokensep + nbinary + tokensep + binary + tokensep + cat
	                        if Dpositions.has_key(poskey):
	                            Dpositions[poskey].append(start)
                                else:
	                            Dpositions[poskey] = [start];

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
	                    poskey = words + tokensep + nbinary + tokensep + binary + tokensep + cat
	                    if Dpositions.has_key(poskey):
	                        Dpositions[poskey].append(start)
                            else:
	                        Dpositions[poskey] = [start];

                # get the next key value
            # end for (key in Grams.keys())

            # reinitialize Grams
            Grams.close()
            Grams = bsddb.btopen(None)

            # print a note to the screen that these n-grams have been indexed.
            print "read in,",
            sys.stdout.flush()

            # -----------------------------
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
                                if nbinary == nbinaries:
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

    # close the Grams file
    Grams.close()
    
Corpus.close()
CorpusPOS.close()
CorpusRel.close()
CorpusWords.close()

if xhtml:
    filename = destination_dir
    print_xhtml_output(filename,output)
