#!/usr/bin/python3
#-*- coding: utf-8 -*-

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, hbar, pi

import re

#def filter_same_keys_values(keyvalue_strings, output_strings=True):
    def filter_same_keys_values(self, keyvalue_strings, output_strings=True):
        """ Seeks for key=value pairs that are shared with among all strings in the list, and removes them if found """
        def try_float_value(tup): 
            """ Whenever possible, safely convert second tuple items (i.e. values) to float """
            if len(tup)==1:             return tup
            elif len(tup)==2:
                try:                    return (tup[0], float(tup[1]))
                except:                 return tup
        ## Split names into "key=value" chunks and  then into ("key"="value") tuples
        keyvaluelists = []
        for keyvalue_string in keyvalue_strings: 
            #print("keyvalue_strings", keyvalue_strings) ## TODO clean up debugging leftovers
            chunklist = re.split('[_ ]', keyvalue_string) 
            #print("    chunklist", chunklist)
            keyvaluelist = [try_float_value(re.split('=', chunk)) for chunk in chunklist] 
            #print("   -> keyvaluelist", keyvaluelist)
            keyvaluelists.append(keyvaluelist)
        ## If identical ("key"="value") tuple found everywhere, remove it 
        for keyvaluelist in keyvaluelists.copy(): 
            for keyvalue in keyvaluelist.copy():
                if all([(keyvalue in testkeyvaluelist) for testkeyvaluelist in keyvaluelists]):
                    for keyvaluelist2 in keyvaluelists:
                        keyvaluelist2.remove(keyvalue)
        ## By default, return simple flat list of strings, otherwise a nested [[(key,value), ...]] structure
        if output_strings:
            ## Generate the strings
                return [' '.join(['='.join([str(v) for v in kvpair]) for kvpair in keyvaluelist]).strip() for keyvaluelist in keyvaluelists]
        else:   return keyvaluelists



#print(filter_same_keys_values(('/home/dominecf/p/plotcommander/test_files/doublecolumn_names.dat conductivity (uS)', '/home/dominecf/p/plotcommander/test_files/doublecolumn_names_parameters.dat Sample Conductivity (uS)'),  output_strings=False))

labels = [
        'batch_Comment=a205Q_AlGaNBarrierX=0.24_AlNSpacer=0.5_GaNSpacer=5_GaNSpacerDopingExp=18_GateBiasScan',
        ]
print(filter_same_keys_values(labels,  output_strings=True))
#print(filter_same_keys_values(labels,  output_strings=True))
#print([x for x in filter_same_keys_values(labels,  output_strings=True)])
#
#labels = ('/home/dominecf/p/plotcommander/bandedges.dat column2',)
#print(filter_same_keys_values(labels,  output_strings=False))
#print(filter_same_keys_values(labels,  output_strings=True))
#print([x for x in filter_same_keys_values(labels,  output_strings=True)])
