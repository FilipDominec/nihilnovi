    def rm_bg(y, iter=50, coef=0.75, blurpx=250):
        """ subtracts smooth slowly varying background, keeping peaks and similar features,
        (almost) never resulting in negative values """
        def edge_safe_convolve(arr,ker): 
            return np.convolve(np.pad(arr,len(ker),mode='edge'),ker,mode='same')[len(ker):-len(ker)]

        y0 = y[:]
        ker = 2**-np.linspace(-2,2,blurpx)**2; 
        for i in range(iter):
          y = edge_safe_convolve(y,ker/np.sum(ker))
          y = y - ( np.abs(y-y0) + y - y0)*coef
        return y0-y

    y=rm_bg(y)
