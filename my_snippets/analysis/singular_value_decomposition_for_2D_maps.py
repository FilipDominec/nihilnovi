## Computes Singular Value Decomposition for (e.g. spectroscopic) data, assuming the number of data sets 
## is integer squared (4,9,16,25...) in total, representing an in NxN array. Plots the results, 
## saves all data.

## Options
ncomponents = 5
decimatex = 1

for n in range(len(ys)): ys[n] -= np.linspace(np.mean(ys[n,:20]), np.mean(ys[n,-20:]), len(ys[n]))
a, xs = ys[:, ::decimatex], xs[:, ::decimatex]  # decimate if matrices too big
U, s, V = np.linalg.svd(a, full_matrices=False) # singular value decomposition!
U, V = U * np.sign(np.sum(V,axis=1)), (V.T * np.sign(np.sum(V,axis=1))).T # fix signs


res = (np.dot(U,np.diag(s)).T)
dim = int(len(res)**.5)   ## assuming the original curves were acquired in a square NxN pattern!
fig.delaxes(ax)
axs = fig.subplots(ncomponents, 2) #axs = [ax for axx in axs for ax in axx] ## flatten

for x, y, label, ax in         zip(xs[:ncomponents], V[:ncomponents], range(ncomponents), axs[:,0]):
    ax.plot(x, y, label="SVD component %d" % (label+1), c='k', lw=.6)
    ax.set_xlabel('wavelength (nm)')
    ax.set_ylabel('spectral intensity')
    ax.legend(loc='best', prop={'size':10})
    np.savetxt('svd-basis.txt', np.vstack([xs[0], V[:ncomponents]]).T, fmt="%.6f")

for compn, ax in enumerate(axs[:,1]):
    ax.set_aspect(aspect=1.0)
    component = res[compn].reshape(dim,dim)
    x,y = np.arange(dim), np.arange(dim)[::-1]
    levels = np.linspace(np.min(component), np.max(component), 50) 
    ax.contourf(x,y,component[::1][::-1], levels=levels, extend='both', cmap=cm.jet)
    cf = ax.contour(x,y,component[::1][::-1], levels=levels, cmap=cm.jet) # avoid white stripes
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(y[0], y[-1])
    fig.colorbar(cf, ax=ax)
    np.savetxt('svd-map-of-component{}.txt'.format(compn+1), (component).T, fmt="%.6f")
    #np.savetxt('svd-map-of-coefficient{}_yflip.txt'.format(compn), (component[:][::-1]).T, fmt="%.6f")
    #np.savetxt('svd-map-of-coefficient{}_xyflip.txt'.format(compn), component, fmt="%.6f")
