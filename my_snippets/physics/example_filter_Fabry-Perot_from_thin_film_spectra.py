def nGaN(energies):
    ## returns index of refraction in GaN according to [Tisch et al., JAP 89 (2001)]
    eV = [1.503, 1.655, 1.918, 2.300, 2.668, 2.757, 2.872, 3.006, 3.136, 3.229, 3.315, 3.395, 3.422] 
    n  = [2.359, 2.366, 2.383, 2.419, 2.470, 2.486, 2.511, 2.549, 2.596, 2.643, 2.711, 2.818, 2.893] 
    return np.interp(energies, eV, n)
for x, y, param, label, xlabel, ylabel, color in         zip(xs, ys, params, labels, xlabels, ylabels, colors):
    ## initially, x is free space wavelength (in nanometers)
    ax.plot(x, y, label="%s" % (label), color='k', lw=.5)
    ## convert x1 to wavenumber in GaN
    x1 = 2*np.pi*nGaN(1239.8/x)/(x*1e-9)   # (1 eV photon has wavelength of 1239.8 nm in vacuum)

    ## interpolate so that the x-axis is in increasing order and equidistant
    x2 = np.linspace(np.min(x1), np.max(x1), len(x1)*4)  ## finer resample to keep all spectral details
    y2 = np.interp(x2, x1[::-1], (y[::-1]))

    ## using FFT, x2 is transformed roughly into "thicknesses of virtual Fabry-Perot resonators"
    xf = np.fft.fftfreq(len(x2), x2[1]-x2[0])
    yf = np.fft.fft(y2)
    #ax.plot(np.fft.fftshift(xf)*1e6, np.fft.fftshift(np.abs(yf)), label="%s" % (label), color=color, lw=1)
    
    ## now find and remove the spectral peak
    findmax = np.argmax(np.abs(yf[20:-20])) + 20
    yf[findmax-5:findmax+5] = (yf[findmax-5] + yf[findmax+5])/2
    yf[len(yf)-findmax-5:len(yf)-findmax+5] = (yf[findmax-5] + yf[findmax+5])/2
    #ax.plot(np.fft.fftshift(xf)*1e6, np.fft.fftshift(np.abs(yf)), label="%s" % (label), color=color, lw=1)

    # invert FFT of spectra and re-interpolate wavenumber in GaN back to wavelength
    y3 = np.interp(2*np.pi*nGaN(1239.8/x)/(x*1e-9), x2, (np.abs(np.fft.ifft(yf))))  ## np.fft.fftshift(xf)
    ax.plot(x, y3, label="%s" % (label), color=color, lw=1.5)
    
ax.set_xlabel('free-space wavelength (nm)')
ax.set_ylabel('thin-film luminescence spectra (A. U.)')
ax.set_ylim(ymin=.3e-1)
ax.set_title('')
