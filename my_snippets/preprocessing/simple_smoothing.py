    def convolve_without_edge_artifacts(ar, ker): 
        # at edges, the curve won't be bent towards 0, but may become more noisy
        norm = np.convolve(np.ones_like(ar), ker, mode='same')
        return np.convolve(ar, ker, mode='same') / norm

    smooth_points = 25 # Select width for the (truncated-Gaussian) smoothing kernel
    smooth_kernel = 2**-np.linspace(-3,3,smooth_points)**2 # Or use any function you like
    smooth_kernel /= np.sum(smooth_kernel) # Roughly maintain the curve height

    y = convolve_without_edge_artifacts(y, smooth_kernel)
