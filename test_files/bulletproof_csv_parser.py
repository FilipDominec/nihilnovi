#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
Why do one need this module instead of e.g. pandas.read_csv('../data/example.csv', header=None) ? 

   
   
1)  Automatic detection of separators in Pandas (option sep=None) currently clashes with options 
    delim_whitespace=True, error_bad_lines=False. This module applies quite a robust detection.
2)  Pandas does not allow different comment characters like "!;,%" in single file
3)  
"""

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


## STRATEGY:    1) detect & filter out comments/parameters      2) detect columns      3) try to find header and match to columns


commentCharsLineStart        = ['#', '!', ';', ',', '%'] 
parameterSeparators          = ['=', ':', '\t*', ',']
commentCharsLineMiddle       = ['#']
parameterSplitterOtherwise   = ['=']
skipHeaderLines              = 0

maxLineLength               = 1024          ## hardly any numeric table in ASCII will have more than one 1kB per line 

headerOrdinateAllowOmit     = True             ## e.g. three-column CSV files sometimes have only two names in header
headerOrdinateSuggestName   = 'x'              ## ... in such a case, the x-axis will be named as such

tryColSeparators    = [',', '\t', '\s', '\s*']
unevenColumnLengthPenalty = 1       ## may be any positive number

def tryFloat(string):
    try:
        float(string)
        return True
    except:
        return False
def floatableLen(arr):
    return len([string for string in arr if  tryFloat(string.strip())])



## Load file
try:
    lines = open(fileName).readlines()
except:
    print('Error: file could not be opened for reading')
    exit()

## Abort if overly long lines
if max([len(line) for line in lines]) > maxLineLength:
    print('Error: a line longer than %d characters - file is probably binary or corrupt' % maxLineLength)
    exit()

## Filter out empty lines, and also all that are commented out. If they have a parameter-like syntax, store them in a dict.
filteredLines = [] 
parameters = {} 
for lineNumber, line in enumerate(lines):
    if line[0:1] in commentCharsLineStart or lineNumber < skipHeaderLines:
        for parameterSeparator in parameterSeparators:
            regExpPar = re.compile(parameterSeparator)
            if parameterSeparator in line[1:-1]:
                paramKey, paramValue = regExpPar.split(line[1:-1], 1)

                parameters[paramKey] = float(paramValue) if tryFloat(paramValue) else paramValue
                break
    else:
        filteredLines.append(line)

## Cut line end after a comment character is found
for commentCharLineMiddle in commentCharsLineMiddle: 
    filteredLines = [line.split(commentCharLineMiddle,1)[0] for line in filteredLines]
print("parameters:", parameters)
print("filteredLines:", filteredLines)


## Detect header (always below comments/parameters and above numbers)
# TODO
# 

## Find the number of columns 
bestColSeparatorFitness = -1000
bestColSeparator = None
for tryColSeparator in tryColSeparators: 

    ## Split each line according to the tryColSeparator; count the data fields that can be converted to float
    ## TODO first column may be header, do not enforce floatability!
    regExp = re.compile(tryColSeparator)
    columnsOnLines = np.array([floatableLen(splitLine) for splitLine in [regExp.split(line.strip()) for line in filteredLines]])

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
    
## Parse the actual numeric data
regExp = re.compile(tryColSeparator)
columnsOnLines = np.array([floatableLen(splitLine) for splitLine in [regExp.split(line.strip()) for line in filteredLines]])
## TODO TO FLOAT -> np.array
