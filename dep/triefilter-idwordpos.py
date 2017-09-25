#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

# This is a preprocessing script for decca-dep.py.  Please see the README
# for details.

# imports

import sys

# -----

def get_position(corpusid):
    wordposition = corpusid.split("_")[1]
    return int(wordposition)

def is_continuous(binary):
    bool = 1
    for i in binary:
        if i == "0":
            bool = 0
    return bool

# -----

def overlap(position1,binary1,position2,binary2):

    """ overlap takes two corpus positions and their binary values
    (reflecting the span of the string there) and sees whether or not
    they overlap """

    position1parts = position1.split("_")
    position2parts = position2.split("_")
    sentid1 = int(position1parts[0][1:])
    sentid2 = int(position2parts[0][1:])
    wordid1 = int(position1parts[1])
    wordid2 = int(position2parts[1])

    # if the binaries are in different sentences, they cannot possibly overlap
    if sentid1 != sentid2:
        return 0

    # the lower positions are simply the starting corpus positions;
    # the higher positions are the ending positions, calculated by
    # seeing how far the binary value stretches
    lower1 = wordid1
    higher1 = wordid1 + len(binary1) - 1
    lower2 = wordid2
    higher2 = wordid2 + len(binary2) - 1
    
    # set bool to false
    bool = 0
    
    # if the lower or higher value falls within the bounds of the
    # other string, they overlap
    if lower1 >= lower2 and lower1 <= higher2:
        bool = 1
    elif higher1 <= higher2 and higher1 >= lower2:
        bool = 1
    elif lower2 >= lower1 and lower2 <= higher1:
        bool = 1
    elif higher2 <= higher1 and higher2 >= lower1:
        bool = 1

    # return 1 or 0
    return bool

# -----

def make_trie(D,list,triple):

    """ make_trie takes a dictionary, a (non-empty) list of elements of a
        constituent, and a triple consisting of the corpus index position
        of the constituent, its category label, and its binary
        representation.  From this, it creates a path in a trie
        (dictionary D) representing the words in list.

        It does this by calling itself with a subdictionary and a
        smaller list of words.        
    """

    # get the first element in the list
    element = list.pop(0)
    if list:

        # if this dictionary ((sub)trie) already has this element,
        # make a recursive call to make_trie with the next subtrie
        # (i.e. next level down in the trie)
        
        if D.has_key(element):
            make_trie(D[element],list,triple)

        # if this element is not in the dictionary, we need to create
        # a new subdictionary (subtrie) which this element will point
        # to (i.e. we're creating a new node in the trie).  The
        # recursive call will build up a trie for us to point to.
        else:
            E = {}
            make_trie(E,list,triple)
            D[element] = E

    # if there are no words left in the list, we have hit bottom and
    # have to add an indication of this: "NONE" is our keyword which
    # indicates a terminal node
    else:
        (index,cat,binary) = triple

        # We need to make sure that "NONE" does not overwrite other
        # branches that D[element] might point to
        if D.has_key(element):

            # We need to make sure that multiple "NONE" values are
            # allowed, for different corpus positions with the same
            # string
            if D[element].has_key("NONE"):

                # We need to make sure that identical strings with the
                # same corpus starting position are not truly
                # identical, i.e. cover the same exact words (as
                # binary tells us)
                if D[element]["NONE"].has_key(index):

                    # if everything is the same, this could be because
                    # multiple labels were assigned (unary branch)
                    if D[element]["NONE"][index].has_key(binary):
                        old_cat = D[element]["NONE"][index][binary]
                        
                        # we want to keep the longer cat label since
                        # this will be the one which represents a
                        # unary branch
                        if len(cat) > len(old_cat):
                            D[element]["NONE"][index][binary] = cat
                        # else do nothing because it already has the
                        # longer category label (old_cat)

                    # Ultimately, we point at the category label
                    else:
                        D[element]["NONE"][index][binary] = cat
                
                # D[element]["NONE"] does not have key index
                else:
                    D[element]["NONE"][index] = {binary:cat}
            # D[element] does not have key "NONE" already
            else:
                D[element]["NONE"] = {index:{binary:cat}}

        # if the element has not been in the dictionary previously,
        # point it to a complex "NONE" value
        else:
            D[element] = {"NONE":{index:{binary:cat}}}

# -----

def find_match(Dictionary,sentence,sentid):
    
    """ find_match takes a Dictionary/Trie, a sentence in list form,
    and a starting position, and walks down the trie to find which
    substrings of the sentence match """

    # loop through the sentence, ensuring that we check for potential
    # strings starting with any word in the sentence
    for index in range(len(sentence)):
        # position is the current corpus position for this given word
        position = "s" + str(sentid) + "_" + str(index + 1)

        # the call to find_match_aux does the bulk of the work
        find_match_aux(Dictionary,sentence,position,index)

def find_match_aux(Dictionary,sentence,position,index,binary="",string=""):

    """ find_match_aux builds up a string and a binary representation
    for words in the sentence by seeing if they match something in the
    Dictionary """

    # proceed only if the index for the word (position within
    # sentence) is actually within bounds

    if index < len(sentence):

        # get the appropriate word to add to the string
        word = sentence[index]
        
        # if the trie has the word, continue following this path: note
        # the effect of pruning the search space if the trie does not
        # have the word.

        if Dictionary.has_key(word):

            # add the word to the string and a "1" to the binary
            # representation (since it has been filled)
            this_string = string + "\t" + word
            this_binary = binary + "1"

            # follow this path: add 1 to index and send string and
            # binary values which have accounted for adding this word
            find_match_aux(Dictionary[word],sentence,position,index+1,this_binary,this_string)

            # Additionally, we check to see if adding a word bottoms
            # out.  If so, we print out all relevant information.
            if Dictionary[word].has_key("NONE"):

                # give NIL values for categories if these strings are
                # not the exact ones found in the trie
                if Dictionary[word]["NONE"].has_key(position):
                    if Dictionary[word]["NONE"][position].has_key(this_binary):
                        cat = Dictionary[word]["NONE"][position][this_binary]
                    else:
                        cat = "NIL"
                else:
                    cat = "NIL"

                this_string = this_string.strip()
                to_print = 1

                if cat == "NIL":
                    for this_index in AllGrams[this_string]:
                        for index_binary in AllGrams[this_string][this_index]:
                            if overlap(this_index,index_binary,position,this_binary):
                                to_print = 0


                if to_print and cat == "NIL":
                    if (not is_continuous(this_binary)) and (not Discontinuity.has_key(this_string)):
                        to_print = 0
                
                if to_print:
                    print str(position) + "\t" + cat + "\t" + this_binary + "\t" + this_string

        # if there have been words up to this point, we need to match the
        # longest string(s), so we make a recursive call

        # note that if string is empty, we cut off any more searching
        # because this means that getting to this word has led
        # nowhere.
            
        if string:

            # add '0' to binary because we are moving up one in the
            # index without adding the corresponding word            
            find_match_aux(Dictionary,sentence,position,index+1,binary + "0",string)

# -----

def add_to_grams(AllGrams,nucleus,index,cat,binary):

    # check to see if this string is already in AllGrams
    if AllGrams.has_key(nucleus):
        # check to see if this index is already in AllGrams
        if AllGrams[nucleus].has_key(index):
            # nb: we are only dealing with true categories when first
            # adding to AllGrams: only one cat per binary should be
            # acceptable
            AllGrams[nucleus][index][binary] = cat
        else:
            # AllGrams[nucleus] does not have key index
            AllGrams[nucleus][index] = {binary:cat}
    else:
        # AllGrams does not have key nucleus
        AllGrams[nucleus] = {index:{binary:cat}}

def add_to_continuity(Discontinuity,nucleus,binary):
    if not is_continuous(binary):
        Discontinuity[nucleus] = 1

# -----

try:
    corpus = sys.argv[1]
    constituents = sys.argv[2]
except:
    print "Usage: " + sys.argv[0] + " input_corpus.conll constituents.txt"
    sys.exit()


# create an empty dictionary (which will be our trie)
Trie = {}

Discontinuity = {}
AllGrams = {}

# open the constituents file and begin reading it
try:
    const = open(constituents,'r')
except:
    sys.stderr.write("\n\nError: Unable to open constituents file " + constituents + "\n")

line = const.readline()

# For each line (i.e. constituent), make a trie branch
while line:
    line = line.strip()
    spl = line.split("\t")

    # after removing the index, cat, and binary values, all that
    # should be left are the words of the constituent
    index = spl.pop(0)
    cat = spl.pop(0)
    binary = spl.pop(0)

    nucleus = "\t".join(spl)
    add_to_grams(AllGrams,nucleus,index,cat,binary)
    add_to_continuity(Discontinuity,nucleus,binary)

    # call make_trie, which will add this constituent to the
    # dictionary Trie
    make_trie(Trie,spl,(index,cat,binary))

    # read the next line
    line = const.readline()

# close constituents file
const.close()

# -----

# Go through corpus and find strings which match the constituents in
# the trie

# initialize variables
sentence = []

# open the corpus and read the first line
try:
    file = open(corpus,'r')
except:
    sys.stderr.write("\n\nError: Unable to open corpus file " + corpus + "\n")
    sys.exit(1)

line = file.readline()

currsentid = 0

# loop through every line in the corpus
while line:
    line = line.strip()
    spl = line.split('\t')

    # get the index and word
    id = spl[0]
    sentid = int(spl[0].split("_")[0][1:])
    if currsentid == 0:
        currsentid = sentid
    word = spl[1]
    tag = spl[2]
        
    # when we hit a new sentence, call find_match with the sentence
    if sentid != currsentid:
        find_match(Trie,sentence,currsentid)

        # reset variables
        sentence = []
	currsentid = sentid

    # append the current word to the sentence
    sentence.append(word)

    # read in the next line
    line = file.readline()

# be sure to find matches for the final sentence
find_match(Trie,sentence,currsentid)

# close the corpus file
file.close()
