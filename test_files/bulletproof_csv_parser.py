#!/usr/bin/env python3
#-*- coding: utf-8 -*-

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.constants import c, hbar, pi

fileName = sys.argv[1]

data_df = pd.read_csv(fileName)
print(data_df.columns)
#colHH = data_df['colHH']
#colHH = data_df.colHH


