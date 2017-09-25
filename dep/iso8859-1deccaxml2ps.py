#!/usr/bin/env python

# DECCA infomation:
#
# Copyright (C) 2006 Markus Dickinson, Detmar Meurers, Adriane Boyd
# Contact: decca@ling.osu.edu
# URL: http://decca.osu.edu
# License: GNU GPL (http://decca.osu.edu/software/license.html)

# This script uses DGgraph (c) 2002-2004 by M.T. Kromann.

import sys
import os
import commands
import locale
import libxml2
import libxslt
import re

"""
Input: DeccaXML

Output: PS dggraph of each sentence

"""

dggraph_header = """
%! (c) 2002 Matthias T. Kromann <mtk@id.cbs.dk>

%% This PostScript library is distributed under the GNU public  
%% license for libraries, as part of the DGgraph package.
%% Please see: http://www.id.cbs.dk/~mtk/DGgraph for source code,
%% documentation and license.

%% 1. DGgraph Prologue

100 dict begin /llx 20 def /lly 20 def /urx 500 def /ury 792 def /LW 1
def /X 2 def /Y 0 def /dO 5 def /dA 10 def /dAW 2.5 def /dAH 6 def
/dAD 2 def /dT 15 def /dB 18 def /dT0 3 def /dB0 8 def /dW 8 def /dH
10 def /dL 20 def /strings 1 def /framegray 1 def /bggray 1 def /nextw
0 def /nexte 0 def /xdef {exch def} def /max {dup 3 -1 roll dup 3 -1
roll lt {pop} {exch pop} ifelse} def /min {dup 3 -1 roll dup 3 -1 roll
gt {pop} {exch pop} ifelse} def /ISOfont {findfont dup length dict
begin {1 index /FID ne {def} {pop pop} ifelse} forall /Encoding
ISOLatin1Encoding def currentdict end definefont pop} def /Helvetica
/Helvetica ISOfont /romanfont /Helvetica findfont 10
scalefont def /smallfont /Helvetica findfont 7 scalefont def
romanfont setfont /qsort {1 index length 0 exch qsortx pop} def
/qsortx {2 copy 2 sub gt {pop pop} {findpivot dup -1 eq {pop pop pop}
{4 index exch get 3 1 roll 2 copy 7 2 roll 1 sub {exch {dup 5 index
exch get 3 index 5 index exec -1 eq {1 add} {exit} ifelse} loop exch
{dup 5 index exch get 3 index 5 index exec -1 gt {1 sub} {exit}
ifelse} loop 2 copy gt {exit} if 2 copy 6 index 3 1 roll switch} loop
3 -1 roll pop pop 5 -1 roll exch dup 6 1 roll qsortx 4 2 roll qsortx}
ifelse} ifelse} def /findpivot {2 copy add 1 sub 2 idiv 4 index 1
index get 1 index 1 1 index 5 index add 6 index sub 1 sub {dup 4 index
ge {4 index add 3 index sub} if dup 7 index exch get 2 index 7 index
exec dup 0 ne {1 eq {3 -1 roll pop -1 3 1 roll exit} {pop -1 3 1 roll
exch exit} ifelse} {pop pop} ifelse} for 2 index -1 eq {3 1 roll pop
pop} {pop pop -1} ifelse} def /switch {2 index 2 index get 3 index 2
index get 4 index exch 6 1 roll 3 1 roll put 3 -1 roll put} def
/intcmp {2 copy lt {pop pop -1} {eq {0} {1} ifelse} ifelse} def /arrow
{dA mul 2 index add gsave 4 copy exch 2 copy 5 index 5 1 roll 5 index
8 -2 roll moveto curveto LW setlinewidth stroke 2 index gt {-1} {1}
ifelse dAH mul 3 1 roll exch moveto dAW 0 rmoveto dAW -2 mul 0 rlineto
dAW exch rlineto closepath fill grestore pop} def /word {0 1 1 strings
{index stringwidth pop max} for X exch X add dW add /X xdef strings 1
add 1 roll strings 1 add array astore currentdict /words known {words
nextw 3 -1 roll put} if /nextw nextw 1 add def} def /edget {3 1 roll 2
copy gt {exch neg} if 3 -1 roll 0 1 5 array astore currentdict /edges
known {edges nexte 3 -1 roll put} if /nexte nexte 1 add def} def
/edgeb {3 1 roll 2 copy gt {exch neg} if 3 -1 roll 0 -1 5 array astore
currentdict /edges known {edges nexte 3 -1 roll put} if /nexte nexte 1
add def} def /xcenter {dup words exch get 0 get exch 1 add dup words
length eq {pop X} {words exch get 0 get} ifelse dW sub add 2 div} def
/edge_heights {[ exch 0 0 0 edge_heights0 {pop} repeat pop pop pop
pop} def /edge_heights0 {{edge_heights1 {true} {edge_heights2} ifelse
{true} {edge_heights3} ifelse {true} {edge_heights4} ifelse not {exit}
if} loop} def /edge_heights1 {dup 2 lt {false} {4 index length 3 eq
{true} {4 index 3 get -1 eq} ifelse} ifelse {5 -1 roll dup 1 get exch
2 get 6 index dup dup 2 get 4 -1 roll max 2 exch put 1 3 -1 roll put 1
sub true} {false} ifelse} def /edge_heights2 {dup 0 gt {4 index length
3 gt {4 index 3 get -1 ne {4 index dup dup 1 get exch 3 get edges exch
get 1 get abs eq {dup dup 2 get 1 add 2 exch dup 4 1 roll put 1 index
3 get edges exch get 3 3 -1 roll 7 index exec put mark exch dup aload
pop counttomark 4 sub -1 roll pop -1 counttomark -1 roll astore pop
pop true} {pop false} ifelse} {false} ifelse} {false} ifelse} {false}
ifelse} def /edge_heights3 {dup 1 gt {5 index 5 index dup 1 get exch 2
get 3 -1 roll 1 get 2 index ne {7 index dup 1 5 -1 roll put dup 2 get
3 -1 roll max 2 exch put 5 -1 roll 1 index 4 add 1 roll 1 sub
edge_heights0 1 add dup 4 add -1 roll 5 1 roll true} {pop pop false}
ifelse} {false} ifelse} def /edge_heights4 {counttomark 1 index 4 add
eq {2 index words length lt {mark 3 index dup 1 add 0 7 index 6 index
{dup edges length ge {exch pop exit} if dup edges exch get dup 0 get 6
index eq {4 get 2 index exec 0 gt{dup 6 1 roll} if 1 add} {pop exch
pop exit} ifelse} loop counttomark 1 add 1 roll counttomark 3 roll ] 6
1 roll 3 1 roll 1 add exch pop 3 -1 roll 1 add 3 1 roll true} {false}
ifelse} {false} ifelse} def /edge_displace {-1 -1 0 0 0 {2 index words
length ge {pop pop pop pop pop exit} if 5 -2 roll pop pop -1 -1 5 2
roll 1 index edges 0 3 -1 roll update_super dup maxedges 1 3 -1 roll
update_super exch edges 0 3 -1 roll displace exch maxedges 1 3 -1 roll
displace 3 -1 roll 1 add 3 1 roll} loop} def /displace {{dup 3 index
length ge {3 1 roll pop pop exit} if 2 index 1 index get dup 3 index
get abs 6 index gt {pop 3 1 roll pop pop exit} if dup ioword 7 index
eq {1 index 3 get 0 gt {8 index} {7 index} ifelse dup -1 eq {pop pop 4
0 put} {7 index -1 2 index 2 index gt {neg exch 3 1 roll} if 4 1 roll
2 index gt 3 1 roll gt and not {neg} if 4 exch put} ifelse} {pop pop}
ifelse 1 add} loop} def /update_super {{dup 3 index length ge {pop pop
pop exit} if 2 index 1 index get dup 3 index get 7 index gt {pop pop
pop pop exit} if dup ioword exch 8 index eq {exch 3 get 0 gt {9 -1
roll pop 8 1 roll} {8 -1 roll pop 7 1 roll} ifelse} {pop pop} ifelse 1
add} loop} def /ioword {dup 0 get exch 1 get dup 0 lt {abs exch} {abs}
ifelse} def /split_lines {split_words split_edges split_pages} def
/split_words {/lines [ urx llx sub 0 0 1 {1 index words length ge {pop
pop pop pop exit} if [2 index 0 5 index 0 0 0 0] 5 1 roll {dup xpos dW
2 div sub dup 4 index sub 5 index gt 2 index words length ge or {exch
4 2 roll pop pop dup 1 add exit} if pop 1 add} loop} loop [words
length edges length X 0 0 0 0] ] def} def /split_edges {0 [] 0 1 lines
length 2 sub {dup 1 add lines exch get 0 get exch lines exch get 0 0 2
index [ 8 2 roll 4 index {dup edges exch get 1 get abs 5 index ge {dup
8 1 roll} if edges exch get 3 get dup 4 -1 roll min 3 1 roll max}
forall {5 index edges length ge {exit} if 5 index edges exch get 0 get
4 index ge {exit} if 5 index edges exch get dup 1 get abs 5 index ge
{6 index 7 1 roll} if 3 get dup 4 -1 roll min 3 1 roll max 6 -1 roll 1
add 6 1 roll} loop 2 index 4 3 -1 roll put 1 index 5 3 -1 roll abs put
3 1 roll pop pop 1 2 index put counttomark 1 add 1 roll ] 2 index 6 2
index put 3 -1 roll 1 3 index put} for pop pop} def /split_pages {ury
lly sub 0 0 1 lines length 2 sub {lines exch get dup line_height 3
index 3 index 2 index add lt {3 -1 roll pop 0 3 1 roll} if exch 3 3
index put add dL add} for pop pop} def /line_height {dup 4 get exch 5
get add dA mul strings dH mul add dB add dT add} def /xpos {dup words
length ge {pop X} {words exch get 0 get} ifelse} def /print_word {1
index 4 index 4 get dA mul sub dT sub 1 index xcenter 4 index add exch
3 -1 roll words exch get dup length 1 exch 1 exch 1 sub {3 -1 roll dH
sub 3 1 roll 1 index exch get dup stringwidth pop 2 div neg 4 index
add 3 index moveto show} for pop pop pop} def /print_edge {edges exch
get 1 index 4 index 4 get dA mul sub 1 index 3 get 0 ge {dup dT sub
dT0 add} {dT sub strings dH mul sub dB sub dup dB0 add} ifelse 2 index
ioword xcenter 6 index add exch xcenter 6 index add dup 4 -1 roll
moveto 3 index 2 get dup stringwidth pop -2 div 0 rmoveto show exch 3
index 4 get dO mul add 3 1 roll 3 index 3 get arrow pop} def
/sort_edges {edges {2 copy 0 get exch 0 get exch intcmp dup 0 ne {3 1
roll pop pop} {pop 1 get abs exch 1 get abs exch intcmp} ifelse} qsort
pop /maxedges edges edges length array copy def maxedges {2 copy 1 get
abs exch 1 get abs exch intcmp dup 0 ne {3 1 roll pop pop} {pop 0 get
exch 0 get exch intcmp} ifelse} qsort pop} def /layout_arcs
{sort_edges {} edge_heights {neg} edge_heights 0 1 edges length 1 sub
{edges exch get 4 0 put} for edge_displace split_lines} def
/print_line {dup lines exch get dup line_height 1 index 2 get dup 4
index 1 add lines exch get 2 get exch sub 3 1 roll llx exch sub 3
index 3 get ury exch sub gsave newpath llx 1 index moveto 3 index 0
rlineto 0 3 index neg rlineto 3 index neg 0 rlineto closepath gsave
bggray setgray fill grestore clip gsave framegray setgray stroke
grestore newpath 4 2 roll pop pop romanfont setfont 2 index 0 get 1 5
index 1 add lines exch get 0 get 1 sub {print_word} for smallfont
setfont 3 index 0 eq {[]} {3 index 1 sub lines exch get 6 get} ifelse
{print_edge} forall 3 index 0 eq {0} {3 index 1 sub lines exch get 1
get} ifelse 1 4 index 1 get 1 sub {print_edge} for grestore pop pop
pop pop} def /print_lines {0 1 lines length 2 sub {dup print_line 1
add lines exch get 3 get 0 eq {showpage} if} for} def /draw
{layout_arcs print_lines} def /setup {array /edges exch def array
/words exch def /nextw 0 def /nexte 0 def /strings exch def} def 
"""

def print_dggraph(sentarray, sentrels, filename):
    fileh = open(filename, "w")
    fileh.write(dggraph_header)
    fileh.write("/strings 3 def\n")
    fileh.write("/words [\n")
    fileh.write("(-) () (0) word\n")
    for i in range(len(sentarray)):
        fileh.write("(" + sentarray[i][1] + ") (" + sentarray[i][2] + ") (" + str(i+1) + ") word\n")
    fileh.write("] def\n\n")
    fileh.write("/edges [\n")
    for i in range(len(sentrels)):
        fileh.write(sentrels[i][0] + " " + sentrels[i][1] + " (" + sentrels[i][2] + ") edget\n")
    fileh.write("] def\n")
    fileh.write("draw end\n")
    fileh.close()

locale.setlocale(locale.LC_ALL, 'de_DE')

try:
    corpus_filename = sys.argv[1]
    destination_dir = sys.argv[2]
    image_file = sys.argv[3]
except: 
    print "Usage: " + sys.argv[0] + " deccaxml-file /output/dir list-of-sentence-ids.txt"
    sys.exit()

try:
    corpus_fileh = open(corpus_filename)
except:
    sys.stderr.write("\n\nError: Unable to open corpus file " + corpus_filename + "\n")
    sys.exit(1)

if destination_dir[len(destination_dir)-1] != "/":
    destination_dir += "/"
if not os.path.exists(destination_dir):
    print commands.getoutput("mkdir " + destination_dir)
    print "Creating directory " + destination_dir

try:
    image_fileh = open(image_file)
    images = image_fileh.readlines()
    image_fileh.close()
except:
    sys.stderr.write("\n\nCouldn't open " + image_file + "\n")
    sys.exit(1)

imagelist = {}
for line in images:
    line = line.strip()
    sentnum = int(line)
    imagelist[sentnum] = 1

xmlfileh = open(corpus_filename)

sentstart = "<sentence "
sentend = "</sentence>"

xmldeclpatt = re.compile("<\?xml.*>")
sentstartpatt = re.compile(sentstart)
sentendpatt = re.compile(sentend)

styledoc = libxml2.parseFile("deccaxml-idwordpos.xsl")
style = libxslt.parseStylesheetDoc(styledoc)

styledoc2 = libxml2.parseFile("deccaxml-rels.xsl")
style2 = libxslt.parseStylesheetDoc(styledoc2)

# read in sentence chunks from deccaxml file and process with xsl
insent = 0
xmldecl = ""
for line in xmlfileh:
  if xmldeclpatt.search(line):
    xmldecl = line.strip()
  if sentstartpatt.search(line):
    sentence = xmldecl + "\n" + line
    insent = 1
    sentarray = []
    sentrels = []
  elif sentendpatt.search(line):
    sentence += line
    xmldoc = libxml2.parseDoc(sentence)
    result = style.applyStylesheet(xmldoc, None)
    plainresult = style.saveResultToString(result)
    rarray = plainresult.splitlines()
    for line in rarray:
      line = line.strip()
      if line:
        lineparts = line.split('\t')
	for i in range(len(lineparts)):
	  lineparts[i] = lineparts[i].replace("(", "\(")
	  lineparts[i] = lineparts[i].replace(")", "\)")
        sentarray.append(lineparts)
	filename = destination_dir + lineparts[0].split("_")[0]
	sentnum = int(lineparts[0].split("_")[0][1:])

    if imagelist.has_key(sentnum):
        xmldoc = libxml2.parseDoc(sentence)
        result = style2.applyStylesheet(xmldoc, None)
        plainresult = style2.saveResultToString(result)
        rarray = plainresult.splitlines()
        for line in rarray:
          line = line.strip()
          if line:
            lineparts = line.split('\t')
	    for i in range(len(lineparts)):
	      lineparts[i] = lineparts[i].replace("(", "\(")
	      lineparts[i] = lineparts[i].replace(")", "\)")
	    sentrels.append(lineparts)

        print_dggraph(sentarray, sentrels, filename + ".ps")
        commands.getstatusoutput("ps2epsi " + filename + ".ps " + filename + ".epsi")
        commands.getstatusoutput("pstoimg -type png -antialias -aaliastext -scale 1.5 " + filename + ".epsi")
        #commands.getstatusoutput("rm " + filename + ".ps")
        #commands.getstatusoutput("rm " + filename + ".epsi")

    xmldoc.freeDoc()
    result.freeDoc()
    insent = 0
  elif insent == 1:
    sentence += line

xmlfileh.close()
