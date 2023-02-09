    ## compute (& plot) Fourier-transformed data
    xf = np.fft.fftshift(np.fft.fftfreq(len(x), x[1]-x[0]))
    yf = np.fft.fftshift(np.fft.fft(y))
    ax.plot(xf, abs(yf), label="%s in frequency domain" % (label), color=color, lw=1)

    ## compute (& plot) inverse Fourier-transformed curve, should overlap original one
    y2 = np.fft.ifft(np.fft.ifftshift(yf))
    ax.plot(x, y2, label="%s converted back" % (label), color=color, lw=1)
