    # Computes 0th moment (=integral), 1st moment (centre of mass) and 2nd moment (RMS width) of a curve
    # inputs:   x,y:    usual numpy arrays with coordinates for single curve
    # outputs:  moments: a 3-tuple of 0th, 1st and 2nd moment 
    def moments(y, x):
        are = np.trapz(y, x);  
        cog = np.trapz(y*x,x)/are
        rms = (np.trapz(y*x**2,x)/are - cog**2)**.5
        return [are, cog, rms]
