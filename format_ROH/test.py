#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
"""

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, hbar, pi

import warnings
warnings.filterwarnings("ignore")

import roh
for ff in [f for f in os.listdir('.') if os.path.isfile(f) and '.roh' in f.lower()]:
    my_roh = roh.Roh.from_file(ff);

    #An inspiration on the header header structure was found here: 
    #https://de.mathworks.com/matlabcentral/fileexchange/37103-avantes-to-matlab?s_cid=ME_prod_FX
    #However, it does not seem correct yet
    rawheader = my_roh.header.rawheader
    labels = ["versionID", "serialnr", "serialnr", "serialnr", "serialnr", "serialnr", "serialnr", "serialnr", "serialnr", "serialnr", "serialnr", "WLX1", "WLX2", "WLX3", "WLX4", "ipixfirst", "ipixlast", "measuremode", "dummy1", "laserwavelength", "laserdelay", "laserwidth", "strobercontrol", "dummy2", "dummy3", "timestamp", "dyndarkcorrection", "smoothpix", "smoothmodel", "triggermode", "triggersource", "triggersourcetype", "NTC1", "NTC2", "Thermistor", "dummy4", "spectrum", "s.inttime", "s.average", "s.integrationdelay "]
    for label, headerbyte in zip(labels, rawheader):
        print(label, headerbyte, chr(headerbyte))

    spec = my_roh.payload.spectrum
    print("data87", spec);

    plt.plot(np.linspace(0,1, len(spec)), spec)


## Simple axes
plt.ylim((-0.1,3e4)); plt.yscale('linear')
#plt.xlim((-0.1,1.1)); plt.xscale('linear')

## ==== Outputting ====
## Finish the plot + save 
plt.xlabel(u"x"); 
plt.ylabel(u"y"); 
plt.grid()
plt.legend(prop={'size':10}, loc='upper right')
plt.show()
#plt.savefig("output.png", bbox_inches='tight')

