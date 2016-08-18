#!/usr/bin/env python3
#-*- coding: utf-8 -*-

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.constants import c, hbar, pi
import re

fileName = sys.argv[1]

#data_df = pd.read_csv(fileName)
#data_df = pd.read_table(fileName, header=None, sep=:T)
#print("\n\nCOLUMNS:\n", data_df.columns)
#print("\n\nVALUES:\n", data_df.values)
#print("\n\nPARAMETERS:\n", data_df.)


#<str>              is unacceptable
#<str><float>    better
#<float>    better
#<float><float>
#<float><float><float>    better than    <float><float>


## STRATEGY:    1) detect & filter out comments=parameters      2) detect columns      3) try to find header and match to columns

tryCommentChar      = ['#', '']
tryColSeparators    = [',', '\t', '\s', '\s*']
unevenColumnLengthPenalty = 1

try:
    lines = open(fileName).readlines()
except:
    print('Error: file could not be opened for reading')



bestColSeparatorFitness = -1000
bestColSeparator = None
for tryColSeparator in tryColSeparators: 
    regExp = re.compile(tryColSeparator)
    def tryFloat(string):
        try:
            float(string)
            return True
        except:
            return False
    def floatableLen(arr):
        return len([string for string in arr if  tryFloat(string.strip())])


    ## Split each line according to the tryColSeparator; count the data fields that can be converted to float
    columnsOnLines = np.array([floatableLen(splitLine) for splitLine in [regExp.split(line.strip()) for line in lines]])

    ## Compute the statistics of "floatable" columns at each line 
    columnsOnLinesAvg = np.sum(columnsOnLines)/len(columnsOnLines)
    columnsOnLinesSD  = np.sum(columnsOnLines**2)/len(columnsOnLines)-columnsOnLinesAvg**2
    tryColSeparatorFitness = columnsOnLinesAvg - unevenColumnLengthPenalty*columnsOnLinesSD

    ## Choose parser settings that give the highest average and simultaneously the lowest deviation for the number of fields per line
    ## Note that use of < instead of <= is important to prefer less greedy regexp (e.g. "\s" over "\s*") and 
    ## to preserve column order even if the table is "hollow", i.e. cells missing in its middle columns
    if bestColSeparatorFitness < tryColSeparatorFitness:
        bestColSeparator, bestColSeparatorFitness  = tryColSeparator, tryColSeparatorFitness
    print(tryColSeparator, columnsOnLines, )

print(bestColSeparatorFitness, bestColSeparator)

    #print([regExp.split(line.strip()) for line in lines]) # DEBUG
    
