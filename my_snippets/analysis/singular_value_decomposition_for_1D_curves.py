plotstyle = "basis"
#plotstyle = "amplitude"
decimatex = 1 # for faster computation
ncomponents = 5

a = ys[:, ::decimatex]
xs = xs[:, ::decimatex]
import np.linalg
U, s, V = np.linalg.svd(a, full_matrices=True)

if plotstyle=="basis":
  for x, y, label in         zip(xs[:ncomponents], V[:ncomponents], range(ncomponents)):
    ax.plot(x, y, label="SVD component %d" % (label+1), lw=5*.5**label)
    ax.set_xlabel(xlabelsdedup)
    ax.set_ylabel(ylabelsdedup)

if plotstyle=="amplitude":
  for y, label in         zip(np.dot(U,np.diag(s)).T, range(ncomponents)):
    ax.plot(range(U.shape[0]), y, marker='s', label="SVD component %d" % (label+1), lw=5*.5**label)
    ax.set_xlabel('dataset number')
    ax.set_ylabel('SVD component amplitude')#!/usr/bin/python3  
#-*- coding: utf-8 -*-

