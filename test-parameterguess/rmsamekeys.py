#!/usr/bin/env python
#-*- coding: utf-8 -*-

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, hbar, pi



innames = [
        'batch_Comment=a205Q_AlGaNBarrierX=0.24_AlNSpacer=0.5_GaNSpacer=5_GaNSpacerDopingExp=18_GateBiasScan',
        'batch_Comment=a206Q_AlGaNBarrierX=0.24_AlNSpacer=0.5_GaNSpacer=10_GaNSpacerDopingExp=18_GateBiasScan',
        'batch_Comment=a205Q_AlGaNBarrierX=0.24_AlNSpacer=1_GaNSpacer=5_GaNSpacerDopingExp=18_GateBiasScan'
        ]

import re
paramdicts = []
for inname in innames:
    paramdict = {}    
    chunks = re.split('[_ ]', inname) 

    for splitchunk in [re.split('=', chunk) for chunk in chunks]:
        if len(splitchunk) == 1:

        paramname_value = dict()
    print(paramname_value)

