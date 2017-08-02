#!/usr/bin/python3
#-*- coding: utf-8 -*-

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, hbar, pi



innames = [
        'batch_Comment=a205Q_AlGaNBarrierX=0.24_AlNSpacer=0.5_GaNSpacer=5_GaNSpacerDopingExp=18_GateBiasScan',
        'batch_Comment=a206Q_AlGaNBarrierX=0.24_AlNSpacer=0.5_GaNSpacer=10_GaNSpacerDopingExp=18_GateBiasScan',
        'batch_Comment=a205Q_AlGaNBarrierX=0.24_AlNSpacer=1__GaNSpacerDopingExp=18_GateBiasScan'
        ]

import re


keyvaluelists = []
def try_float_value(tup): ## Whenever possible, converts values to floats
    if len(tup)==1:             return tup
    elif len(tup)==2:
        try:                    return (tup[0], float(tup[1]))
        except:                 return tup
for inname in innames:
    #print("inname", inname) ## TODO clean up debugging leftovers
    chunklist = re.split('[_ ]', inname) ## Split names into "key=value" chunks
    #print("    chunklist", chunklist)
    keyvaluelist = [try_float_value(re.split('=', chunk)) for chunk in chunklist] ## Split names into (key="value") tuples
    #print("   -> keyvaluelist", keyvaluelist)
    keyvaluelists.append(keyvaluelist)
for keyvaluelist in keyvaluelists:
    for keyvalue in keyvaluelist:
        if all([(keyvalue in testkeyvaluelist) for testkeyvaluelist in keyvaluelists]):
            for keyvaluelist2 in keyvaluelists:
                keyvaluelist2.remove(keyvalue)
#for kv in keyvaluelists: #print("KEYVALUELISTS", kv)
