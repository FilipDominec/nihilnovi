#!/usr/bin/python3
#-*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from mpl_toolkits.axes_grid1 import host_subplot

fig = plt.figure(figsize=(7,4), dpi=96, facecolor='#eeeeee', tight_layout=1)
ax = host_subplot(111)

x = np.arange(0., 10., 0.1)
ax.plot(x, 12+x**1.5+0.1*x**2.5)

ax.set_xlabel('expected maximum load (kg)')
ax.set_ylabel('needed bar diameter (cm)')

ax2 = ax.twin()
ax2.set_ylabel('bar cross-section (cm$^{2}$)')


def tick_function(r,q=0): return 10.46*(r**1.68)
#def tick_function_inv(r): return ((r/10.46)**(1/1.68))
from scipy.optimize import brentq
def tick_function_inv(r): 
    return brentq(lambda r, q: tick_function(r) - q, 0, 20000, 1e6)

print('tick_function_inv', tick_function_inv(2000))
print('tick_function_inv', tick_function_inv(10000))


ylim2 = ax.get_ylim()
ax2.set_ylim([tick_function(ax.get_ylim()[0]), tick_function(ax.get_ylim()[1])])
yticks2=ax2.get_yticks() 
ax2.set_ylim(ylim2)

label_pos_legend = [[tick_function_inv(0,ytick2), ytick2] for ytick2 in yticks2]
pos, legend = zip(*label_pos_legend[:-1])  ## last value left out, since it shifted the upper ax2 limit
print(pos, legend)
ax2.set_yticks(pos)


#ax2.yaxis.set_major_formatter(FuncFormatter(lambda r, _: r**2 + 0.123))
ax2.yaxis.set_major_formatter(FuncFormatter(lambda r, _: tick_function(r)))
#ax2.axis['top'].major_ticklabels.set_visible(False)


















ax.legend(prop={'size':10}, loc='upper right')
ax.grid()

plt.show()
