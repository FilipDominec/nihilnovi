
    # Simple data fitting by a given function
    # inputs:   x,y:    usual numpy arrays with coordinates for single curve
    #           p0:     initial values of parameters
    #           fitf(): function to be fitted with: a Gaussian by default, but edit it to your needs
    # outputs:  popt:   parameters of the best fit
    def fitf(x, A, x0, FWHM): return A * np.exp(-(x-x0)**2 / (FWHM/2)**2 * np.log(2))
    p0 = (.01, 450, 20)      
    from scipy.optimize import curve_fit
    popt, pcov = curve_fit(fitf, x, y, p0)
    print(popt, label)
    ax.plot(x, fitf(x, *popt), color='k', linestyle='--', linewidth=0.5)  # plots the fitted curve

