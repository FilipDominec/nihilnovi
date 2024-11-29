def retouch_outliers(y, sigma_criterion=3):
    kernel = [1,0,1] # averaging of neighbors #kernel = np.exp(-np.linspace(-2,2,5)**2) ## Gaussian
    kernel /= np.sum(kernel)                        # normalize
    smooth = np.convolve(y, kernel, mode='same')    # find the average value of neighbors
    rms_noise = np.average((y[1:]-y[:-1])**2)**.5   # estimate what the average noise is (rms derivative)
    outlier_mask = (np.abs(y-smooth) > rms_noise*sigma_criterion)    # find all points with difference from average less than 3sigma
    y[outlier_mask] = smooth[outlier_mask]
    return y
