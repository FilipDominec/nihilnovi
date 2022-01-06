#!/usr/bin/python3
#-*- coding: utf-8 -*-
"""
Usual sorting algorithms do not care much about the numerical values embedded in a string.
This means e.g. that 'temperature-12' may wrongly come after 'temperature12', or '12200fish' will in 
most cases come after '0.123E+05fish'. For scientific data manipulation, this is not satisfactory.

This module offers the sort_alpha_numeric() function which accepts a list of strings. For each of them,
it uses a regular expression to split it into a sub-list of interleaved non-numeric and numeric sections, the 
latter being converted to true float numbers. Then, the proper order of these sub-lists can be efficiently found, 
and the original names are returned. 

To test the intelligent alpha-numeric sorting, try to call it add arguments as such:
>>> python3 sort_alpha_numeric.py xx-123.4zz xx-1.233e+002yy xx-123.2yy xx-123.4yy
"""

import re
def generate_numeric_pairs(instring):
    span0, span2 = 0, 0
    for match in re.finditer('[-+]?(((\d+(\.\d*)?)|(\.\d+))([eE][+-]?\d+)?)', instring):
        span1, span2 = match.span()
        if span0==span1: span1+=1 ## strip hyphen if number follows a number (it is probably a date like "YYYY-MM-DD")
        yield instring[span0:span1], float(instring[span1:span2])   ## non-numeric part and numeric part
        span0 = span2
    if len(instring)>0 and span2<len(instring):
        yield instring[span2:], 0                  ## do not forget the last non-numeric part, pad with zero
def split_alpha_numeric(instring):
    return list(generate_numeric_pairs(instring))
def split_alpha_numeric_lowercase(instring):
    return [(s[0].lower(), s[1]) for s in list(generate_numeric_pairs(instring))]

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(__doc__)     
    else:
        print("Unsorted:")
        print(sys.argv[1:])
        print("\nSorted:")
        print(sorted(sys.argv[1:], key=split_alpha_numeric))
