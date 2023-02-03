    WIDTH = 25 # points for (truncated-Gaussian) smoothing kernel
    convol = 2**-np.linspace(-2,2,WIDTH)**2
    y = np.convolve(y,convol/np.sum(convol), mode='same') ## simple smoothing
