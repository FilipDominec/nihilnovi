def half_max_x(x, y, half=0.5):
    """ returns two points at X: where the curve first rises above half maximum, and where it last drops below it """
    halfmax = max(y)*half
    signs = np.sign(np.add(y, -halfmax))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]
    return [lin_interp(x, y, zero_crossings_i[0], halfmax),
            lin_interp(x, y, zero_crossings_i[1], halfmax)]
