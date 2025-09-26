    ## Moving average -> near-lossless decimation (takes few ms)
    # TODO Needs fixing? 
    subdiv = 5 # reduce point number by 5 
    convol = np.ones(subdiv)/subdiv  # optionally, quasi-Gaussian smoothing 2**-np.linspace(-1,1,subdiv)**2
    x = x[int(subdiv/2):-int(subdiv/2):subdiv] # + (E[1]-E[0])*subdiv/2 # requires x to be equidistant
    y = np.convolve(y, convol/np.sum(convol), mode='valid')[::subdiv] 
