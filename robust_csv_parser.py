#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
robust_csv_parser.py

Python offers many functions to load a text file containing numbers, e.g. numpy.genfromtxt(), csv.reader() and pandas.read_table().
The reason why I spent two days writing a robust alternative is that the mentioned functions are not flexible enough to recognize 
automatically the syntax of all data files which I encounter in my daily practice. 

This module implements following improvements:
1)  Automatic detection of column separators. This is also implemented by pandas.read_table() as option sep=None), but this currently 
    clashes with the options delim_whitespace=True, error_bad_lines=False. This module employs quite a robust detection.
2)  It allows different comment characters like "!;,%" in a single file. Useful, but probably not implemented elsewhere.
3)  It (usually) aborts reading binary files rather soon. In pandas, it can take a lot of time when one accidentally feeds it 
    with a big binary file.
4)  It recognizes parameters in the file header, and returns them as a dict.
5)  If not specified otherwise, it does not clog the stderr with error reports .

# TODO https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
"""

## Import common moduli
import matplotlib, sys, os, stat
import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd
from scipy.constants import c, hbar, pi
import re
import warnings     
with warnings.catch_warnings(): warnings.simplefilter("ignore")




verbose                     = False
very_verbose                = False

commentCharsLineStart       = ['#', '!', ';', ',', '%']  # if line starts with one of these characters, it will be a comment (or header)
parameterSeparators         = ['=', '\t', ':', ',']     # if line is a comment AND contains one of these, it is parsed as a parameter of the file
commentCharsLineMiddle      = ['#']                      # everything after this character is omitted
parameterSplitterOtherwise  = ['=']                      # if line contains this character, it is parsed as a parameter of the file
strict_table_layout         = False                      # when True, doubled column separators will always imply that the field was left empty

maxLineLength               = 10000             # hardly any numeric table in ASCII will have more than one 10kB per line 

headerOrdinateAllowOmit     = True              # e.g. three-column CSV files sometimes have only two names in header
headerOrdinateSuggestName   = 'x'               # ... in such a case, the first column name will added 

tryColSeparators    = [',', '\t', '\s', '\s+']           # possible ways of separating columns: comma, tabulator, 1 whitespace character, whitespace
## TODO test avoiding escaped whitespace, e.g. use "[^\\]\s" instead of "\s"
unevenColumnLengthPenalty = 1                   # may be any positive number; low value may lead to joining cells, higher value may lead to empty cells detected

guessHeaderSpaces           = True              # Will try to expand CamelCase and unit names with spaces for better look of plots

def safe_float(string):
    try:                    return float(string)
    except:                 return np.NaN
def can_float(string):
    try:    float(string);  return True            ## note: "nan" counts the same as a number
    except:                 return False 
def filter_floats(arr):     return [safe_float(field) for field in arr if      can_float(field)]
def filter_non_floats(arr): return [           field  for field in arr if (not can_float(field) and field!="")]
def floatableLen(arr):      return len(filter_floats(arr))



def loadtxt(file_name, sizehint=None):
    ## Load file
    try:
        lines = open(file_name).readlines(sizehint)
        if verbose: print("Read %d lines" % len(lines))
    except:
        raise IOError('file %s could not be opened for reading' % file_name)

    ## Abort if overly long lines
    if len(lines)>0 and max([len(line) for line in lines]) > maxLineLength:
        raise IOError('Error: a line longer than %d characters found, the file is probably binary or corrupt' % maxLineLength)

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

                    parameters[paramKey.strip()] = float(paramValue) if (safe_float(paramValue) is not np.NaN) else paramValue.strip()
                    break
        else:
            if firstNonSkippedLine is None: firstNonSkippedLine = lineNumber
            filteredLines.append(line)
            skippedLinesN += 1
    if firstNonSkippedLine is None: raise RuntimeError("Error: file empty or all lines in the file identified as comments")
    if very_verbose: print("firstNonSkippedLine", firstNonSkippedLine)

    ## Cut line end after a comment character is found
    for commentCharLineMiddle in commentCharsLineMiddle: 
        filteredLines = [line.split(commentCharLineMiddle,1)[0] for line in filteredLines]
    ## Remove empty lines (which could otherwise confuse the column number estimator)
    filteredLines = [line for line in filteredLines if line.strip()!=""]
    if very_verbose: print("filteredLines:", filteredLines)


    ## Find the number of columns 
    resultingColSeparatorFitness = None
    for tryColSeparator in tryColSeparators: 

        ## Split each line according to the tryColSeparator; count the data fields that can be converted to float
        ## TODO first column may be header, do not enforce floatability!
        regExpSep = re.compile(tryColSeparator)
        ## In the case of tables of a very strict layout, duplicate separator or non-number field would represent a numpy.NaN value
        chosen_len_fn = len if strict_table_layout else floatableLen
        ## (In the following, the inner comprehension returns a list of fields per each line; the outer comprehension assigns 
        ## the whole line with the count of numbers it appears to contain. This naturally depends on our choice of the field separator.)
        columnsOnLines = np.array([chosen_len_fn(splitLine) for splitLine in [regExpSep.split(line.strip()) for line in filteredLines]])

        ## If the first column is header, do not let it spoil the column-number statistics
        if len(columnsOnLines)>1 and columnsOnLines[0]==0: columnsOnLines = columnsOnLines[1:]

        ## Compute the statistics of numeric-valued columns at each line 
        columnsOnLinesAvg = np.sum(columnsOnLines)/len(columnsOnLines)
        columnsOnLinesSD  = np.sum(columnsOnLines**2)/len(columnsOnLines)-columnsOnLinesAvg**2
        tryColSeparatorFitness = columnsOnLinesAvg - unevenColumnLengthPenalty*columnsOnLinesSD

        ## Choose parser settings that give the highest average and simultaneously the lowest deviation for the number of fields per line
        ## Note that use of < instead of <= is important to prefer less greedy regexp (e.g. "\s" over "\s*") and 
        ## to preserve column order even if the table is "hollow", i.e. cells missing in its middle columns
        if resultingColSeparatorFitness is None or resultingColSeparatorFitness  < tryColSeparatorFitness:
            resultingColSeparator           = tryColSeparator
            resultingColSeparatorFitness    = tryColSeparatorFitness
            resultingColumnsOnLines         = int(columnsOnLinesAvg+0.99)        ## (rounding up favors keeping more data whenever possible)
        if very_verbose:
            print("tryColSeparator columnsOnLines, columnsOnLinesAvg, int(columnsOnLinesAvg+0.99), tryColSeparatorFitness, "+
                    "resultingColumnsOnLines", 
                    tryColSeparator, columnsOnLines, columnsOnLinesAvg, int(columnsOnLinesAvg+0.99), tryColSeparatorFitness,
                    resultingColumnsOnLines)
    if resultingColumnsOnLines == 0: raise RuntimeError("Error: estimated that there are zero data columns")
    if very_verbose: print("resultingColSeparator, resultingColumnsOnLines", resultingColSeparator, resultingColumnsOnLines)

        
    ## Detect the header in the last commented line before the data start; if the file contains no comments, try its very first line
    maybeHeaderLine = lines[firstNonSkippedLine-1 if firstNonSkippedLine > 0 else 0]
    while maybeHeaderLine[:1] in commentCharsLineStart  and  maybeHeaderLine != "":  maybeHeaderLine = maybeHeaderLine[1:] # strip comment-out
    regExpSep = re.compile(resultingColSeparator)
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
        if verbose: 
           warnings.warn(("Warning: found %d labels in header for total %d columns; truncating or adding next by the " +
                "rule 'x, column1, column2...'") % (len(columnsInHeader), resultingColumnsOnLines), RuntimeWarning)
    if len(columnsInHeader)==0 and resultingColumnsOnLines==1: columnsInHeader = ['values']
    if len(columnsInHeader) == resultingColumnsOnLines-1: columnsInHeader = ['x'] + columnsInHeader

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
                lcol, rcol = column.rsplit('[',1)
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

    assert len(data_array) >= 1
    assert len(expandedColumnsInHeader) == len(data_array[0])
    if very_verbose:
        print("data_array, expandedColumnsInHeader, parameters", data_array, expandedColumnsInHeader, parameters)
    return data_array, expandedColumnsInHeader, parameters


if __name__ == "__main__":
    fileName = sys.argv[1]
    data_array, header, parameters = loadtxt(fileName)
    print("DATA:",          data_array)
    print("HEADER:",        header)
    print("PARAMETERS:",    parameters)

