
    # Simple data fitting by a given function
    # inputs:   x,y:    usual numpy arrays with coordinates for single curve
    #           p0:     initial values of parameters
    #           Gauss(): function to be fitted with, rename & edit it to your needs
    # outputs:  popt:   parameters of the best fit
    def Gauss(x, A, x0, FWHM): return A*np.exp(-(x-x0)**2/FWHM**2 *4*np.log(2))
    p0 = (.01, 450,20)      
    from scipy.optimize import curve_fit
    popt, pcov = curve_fit(Gauss, x, y, p0)
    print(popt, label)
    ax.plot(x, Gauss(x, *popt), c='k')  # plots the fitted curve

