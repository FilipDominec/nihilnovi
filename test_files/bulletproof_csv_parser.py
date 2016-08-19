#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
Why do one need this module instead of e.g. pandas.read_csv('../data/example.csv', header=None) ? 

   
   
1)  Automatic detection of separators in Pandas (option sep=None) currently clashes with options 
    delim_whitespace=True, error_bad_lines=False. This module employs quite a robust detection.
2)  Pandas does not allow different comment characters like "!;,%" in single file
3)  It takes unacceptable time when it is erroneously fed with a big binary file
4)  
"""

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd
from scipy.constants import c, hbar, pi
import re
import warnings     # TODO warnings.warn("deprecated", DeprecationWarning)
with warnings.catch_warnings(): warnings.simplefilter("ignore")
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

verbose = True
very_verbose = 1

commentCharsLineStart       = ['#', '!', ';', ',', '%'] 
parameterSeparators         = ['=', ':', '\t+', ',']
commentCharsLineMiddle      = ['#']
parameterSplitterOtherwise  = ['=']
strict_table_layout         = False

maxLineLength               = 1024          ## hardly any numeric table in ASCII will have more than one 1kB per line 

headerOrdinateAllowOmit     = True             ## e.g. three-column CSV files sometimes have only two names in header
headerOrdinateSuggestName   = 'x'              ## ... in such a case, the x-axis will be named as such

tryColSeparators    = [',', '\t', '\s', '\s+']      ## TODO test avoiding escaped whitespace, e.g. use "[^\\]\s" instead of "\s"
unevenColumnLengthPenalty = 1       ## may be any positive number

guessHeaderSpaces           = True          ## Will try to expand CamelCase and unit names with spaces for better look of plots

def safe_float(string):
    try:
        return float(string)
    except:
        return np.NaN
def can_float(string):
    try:
        float(string)
        return True            ## note: "nan" counts the same as a number
    except:
        return False 
def filter_floats(arr):     return [safe_float(field) for field in arr if      can_float(field)]
def filter_non_floats(arr): return [           field  for field in arr if (not can_float(field) and field!="")]
def floatableLen(arr):
    return len(filter_floats(arr))



## Load file
try:
    lines = open(fileName).readlines()
except:
    print('Error: file could not be opened for reading'); exit()

## Abort if overly long lines
if max([len(line) for line in lines]) > maxLineLength:
    print('Error: a line longer than %d characters - file is probably binary or corrupt' % maxLineLength); exit()

## Filter out empty lines, and also all that are commented out. If they have a parameter-like syntax, store them in a dict.
filteredLines = [] 
parameters = {} 
skippedLinesN = 0
firstNonSkippedLine = None
for lineNumber, line in enumerate(lines):
    if line[0:1] in commentCharsLineStart:
        for parameterSeparator in parameterSeparators:
            regExpPar = re.compile(parameterSeparator)
            if parameterSeparator in line[1:-1]:
                paramKey, paramValue = regExpPar.split(line[1:-1], 1)

                parameters[paramKey] = float(paramValue) if (safe_float(paramValue) is not np.NaN) else paramValue
                break
    else:
        if firstNonSkippedLine is None: firstNonSkippedLine = lineNumber
        filteredLines.append(line)
        skippedLinesN += 1
if firstNonSkippedLine is None: print("Error: all lines in the file identified as comments"); quit()
if very_verbose: print("firstNonSkippedLine", firstNonSkippedLine)

## Cut line end after a comment character is found
for commentCharLineMiddle in commentCharsLineMiddle: 
    filteredLines = [line.split(commentCharLineMiddle,1)[0] for line in filteredLines]
if very_verbose: print("filteredLines:", filteredLines)


## Find the number of columns 
resultingColSeparatorFitness = -np.infty
for tryColSeparator in tryColSeparators: 

    ## Split each line according to the tryColSeparator; count the data fields that can be converted to float
    ## TODO first column may be header, do not enforce floatability!
    regExpSep = re.compile(tryColSeparator)
    ## In the case of tables of a very strict layout, duplicate separator or non-number field would represent a numpy.NaN value
    chosen_len_fn = len if strict_table_layout else floatableLen
    ## (In the following, the inner comprehension returns a list of fields per each line; the outer comprehension assigns 
    ## the whole line with the count of numbers it appears to contain. This naturally depends on our choice of the field separator.)
    columnsOnLines = np.array([chosen_len_fn(splitLine) for splitLine in [regExpSep.split(line.strip()) for line in filteredLines]])

    ## Compute the statistics of numeric-valued columns at each line 
    columnsOnLinesAvg = np.sum(columnsOnLines)/len(columnsOnLines)
    columnsOnLinesSD  = np.sum(columnsOnLines**2)/len(columnsOnLines)-columnsOnLinesAvg**2
    tryColSeparatorFitness = columnsOnLinesAvg - unevenColumnLengthPenalty*columnsOnLinesSD
    print(columnsOnLines, columnsOnLinesAvg, unevenColumnLengthPenalty,int(columnsOnLinesAvg+0.5))

    ## Choose parser settings that give the highest average and simultaneously the lowest deviation for the number of fields per line
    ## Note that use of < instead of <= is important to prefer less greedy regexp (e.g. "\s" over "\s*") and 
    ## to preserve column order even if the table is "hollow", i.e. cells missing in its middle columns
    if resultingColSeparatorFitness < tryColSeparatorFitness:
        resultingColSeparator           = tryColSeparator
        resultingColSeparatorFitness    = tryColSeparatorFitness
        resultingColumnsOnLines         = int(columnsOnLinesAvg+0.99)        ## (rounding up favors keeping more data whenever possible)
if resultingColumnsOnLines == 0: print("Error: estimated that there are zero data columns"); quit()
if very_verbose: print("resultingColSeparator, resultingColumnsOnLines", resultingColSeparator, resultingColumnsOnLines)

    
## Detect the header in the last commented line before the data start; if the file contains no comments, try its very first line
maybeHeaderLine = lines[firstNonSkippedLine-1 if firstNonSkippedLine > 0 else 0]
while maybeHeaderLine[:1] in commentCharsLineStart  and  maybeHeaderLine != "":  maybeHeaderLine = maybeHeaderLine[1:] # strip comment-out
regExpSep = re.compile(resultingColSeparator)
print(regExpSep.split(maybeHeaderLine.strip()))
columnsInHeader = filter_non_floats(regExpSep.split(maybeHeaderLine.strip()))

## If the header consists of all number-like fields, do not consider it a header (in all cases; no matter if commented out or not)
if very_verbose: 
    print("columnsInHeader,len(columnsInHeader), floatableLen(columnsInHeader)", 
    columnsInHeader,len(columnsInHeader), floatableLen(columnsInHeader))
if floatableLen(columnsInHeader) == len(columnsInHeader): 
    columnsInHeader = [] 

if very_verbose: print("columnsInHeader after search", columnsInHeader)

## Match the header length to the detected column number
if len(columnsInHeader) != resultingColumnsOnLines:   
    if verbose: print("Warning: found %d labels in header for total %d columns; truncating or adding next by the rule 'x, column1, column2...'" % 
            (len(columnsInHeader), resultingColumnsOnLines))
if columnsInHeader == [] and resultingColumnsOnLines>0: columnsInHeader = ['x']
while len(columnsInHeader) < resultingColumnsOnLines:           ## extend it if shorter
    columnsInHeader.append("column%d"%len(columnsInHeader))
columnsInHeader = columnsInHeader[:resultingColumnsOnLines]     ## truncate it if longer

if very_verbose: print("columnsInHeader after label adjustment to columns", columnsInHeader)

## Formatting of the header fields: Convert e.g. "sampleTemperature(K)" to "sample temperature (K)"
expandedColumnsInHeader = []
def camel_case_split(identifier): # from http://stackoverflow.com/a/29920015/1615108
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0).lower() for m in matches]
if guessHeaderSpaces:
    for column in columnsInHeader:
        if   "(" in column[:-2]  and  ")" in column[-1:]: 
            lcol, rcol = column.rsplit('(',1)
            column = " (".join([" ".join(camel_case_split(lcol)), rcol]) 
        elif "[" in column[:-2]  and  "]" in column[-1:]: 
            lcol, rcol = column.rsplit('(',1)
            column = " [".join([" ".join(camel_case_split(lcol)), rcol]) 
        else:
            column = " ".join(camel_case_split(column))
        #if "[" in column[:-2]  and  "]" in column[-1:]: column = " [".join(column.rsplit('[',1)) 
        expandedColumnsInHeader.append(column)
if very_verbose: print("expandedColumnsInHeader", expandedColumnsInHeader)
#columnsInHeaderFloatableN   = [1-floatable(splitLine) for splitLine in [regExpSep.split(line.strip()) for line in filteredLines])
if very_verbose: print('firstNonSkippedLine is #%d and contains: "%s "' % (firstNonSkippedLine, maybeHeaderLine.strip()))


## Parse the actual numeric data
table_values = []
for line in filteredLines:
    line_values = [safe_float(field) for field in filter_floats(regExpSep.split(line.strip()))]
    while len(line_values) < resultingColumnsOnLines: line_values.append(np.NaN)    ## extend line if shorter
    line_values = line_values[:resultingColumnsOnLines]     ## truncate line if longer
    if line_values[0] is not np.NaN: ## todo fix - this is only to prevent an uncommented header adding a [NaN, NaN] first line in data
        table_values.append(line_values)

data_array = np.array(table_values)

if verbose: 
    print("\n")
    print("PARAMETERS:", parameters)
    print("HEADER:", expandedColumnsInHeader)
    print("DATA:",   data_array)

assert len(data_array) >= 1
assert len(expandedColumnsInHeader) == len(data_array[0])


#columnsOnLines = np.array([floatableLen(splitLine) for splitLine in [regExpSep.split(line.strip()) for line in filteredLines]])
## TODO TO FLOAT -> np.array
