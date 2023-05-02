    ## assuming, e.g., that 8 datasets are selected and NGROUP=2, the first four get the same coloring order as the last four
    ## but these two groups are told apart through dashed lines
    NGROUP = 2
    ax.plot(x, y/(1e0 if n<5 else 1), label="%s" % (label), color=colors[n%(len(xs)//NGROUP)*NGROUP], ls=['-','--'][n//(len(xs)//NGROUP)])


