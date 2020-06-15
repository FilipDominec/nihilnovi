
    # Simple data fitting by a given function
    # inputs:   x,y:    usual numpy arrays with coordinates for single curve
    #           p0:     initial values of parameters
    #           fitf(): function to be fitted with: a Gaussian by default, but edit it to your needs
    # outputs:  popt:   parameters of the best fit
    #           stored_popt:   all fit parameters (in case of multiple curves, they may make an interesting
    #                          function of the curves parameter 'param')
    def fitf(x,    A,   x0,  FWHM): return A * np.exp(-(x-x0)**2 / (FWHM/2)**2 * np.log(2))
    p0 =          (.01, 450, 20  )      
    from scipy.optimize import curve_fit
    popt, pcov = curve_fit(fitf, x, y, p0)
    ax.plot(x, fitf(x, *popt), color='k', linestyle='--', linewidth=0.5)  # plots the fitted curve
    stored_popt = np.array([param]+popt) if 'stored_popt' not in locals() else np.vstack((stored_popt.T, [param]+popt)).T
    import inspect; np.savetxt('fitted_parameters.dat', np.vstack([stored_popt]).T, header='\t'.join(['param']+inspect.getargspec(fitf).args[1:])) 

    

