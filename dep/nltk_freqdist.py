# This is a minimal version of FreqDist adapted from the Natural Language
# Toolkit (NLTK) adapted by Adriane Boyd for the DECCA project (June 2006).

# NLTK infomation:
#
# Copyright (C) 2001 University of Pennsylvania
# Author: Edward Loper <edloper@gradient.cis.upenn.edu>
#         Trevor Cohn <tacohn@cs.mu.oz.au> (additions)
# URL: <http://nltk.sf.net>
# License: http://nltk.sourceforge.net/license.html

##//////////////////////////////////////////////////////
##  Frequency Distributions
##//////////////////////////////////////////////////////

class FreqDist:
    """
    A frequency distribution for the outcomes of an experiment.  A
    frequency distribution records the number of times each outcome of
    an experiment has occured.  For example, a frequency distribution
    could be used to record the frequency of each word type in a
    document.  Formally, a frequency distribution can be defined as a
    function mapping from each sample to the number of times that
    sample occured as an outcome.

    Frequency distributions are generally constructed by running a
    number of experiments, and incrementing the count for a sample
    every time it is an outcome of an experiment.  For example, the
    following code will produce a frequency distribution that encodes
    how often each word occurs in a text:
    
        >>> fdist = FreqDist()
        >>> for token in text_token['SUBTOKENS']:
        ...    fdist.inc(token['TEXT'])
    """
    def __init__(self):
        """
        Construct a new empty, C{FreqDist}.  In particular, the count
        for every sample is zero.
        """
        self._count = {}
        self._N = 0

    def inc(self, sample, count=1):
        """
        Increment this C{FreqDist}'s count for the given
        sample.
        
        @param sample: The sample whose count should be incremented.
        @type sample: any
        @param count: The amount to increment the sample's count by.
        @type count: C{int}
        @rtype: None
        @raise NotImplementedError: If C{sample} is not a
               supported sample type.
        """
        if count == 0: return
        
        self._N += count
        self._count[sample] = self._count.get(sample,0) + count

    def N(self):
        """
        @return: The total number of sample outcomes that have been
          recorded by this C{FreqDist}.  For the number of unique 
          sample values (or bins) with counts greater than zero, use
          C{FreqDist.B()}.
        @rtype: C{int}
        """
        return self._N

    def samples(self):
        """
        @return: A list of all samples that have been recorded as
            outcomes by this frequency distribution.  Use C{count()}
            to determine the count for each sample.
        @rtype: C{list}
        """
        return self._count.keys()

    def count(self, sample):
        """
        Return the count of a given sample.  The count of a sample is
        defined as the number of times that sample outcome was
        recorded by this C{FreqDist}.  Counts are non-negative
        integers.
        
        @return: The count of a given sample.
        @rtype: C{int}
        @param sample: the sample whose count
               should be returned.
        @type sample: any.
        """
        return self._count.get(sample, 0)
