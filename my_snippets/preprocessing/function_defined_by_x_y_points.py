def piecewise_linear(x):
    ## returns a piecewise linear function given by points
    ## e.g. here optical index of refraction in GaN: n(eV) according to [Tisch et al., JAP 89 (2001)]
    x_points = [1.503, 1.655, 1.918, 2.300, 2.668, 2.757, 2.872, 3.006, 3.136, 3.229, 3.315, 3.395, 3.422]
    y_points = [2.359, 2.366, 2.383, 2.419, 2.470, 2.486, 2.511, 2.549, 2.596, 2.643, 2.711, 2.818, 2.893]
    return np.interp(x, x_points, y_points)
