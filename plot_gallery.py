## This is a gallery of selected plot types. The xs, ys and other arrays are loaded upon selection
## of files in nihilnovi. Please refer to https://matplotlib.org/gallery/index.html for more examples.
matplotlib.rc('font', size=9, family='serif')
ax.remove(); axs = fig.subplots(3, 4) # prepare for multiple subplots

ax = axs[0,0]; ax.set_title('Scatter X, Y (+legend)') 
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
    ax.scatter(x, y, label="%s" % (label), c=color, marker='od^sph'[n%6], edgecolor='k')
ax.legend(loc='best', prop={'size':10})

ax = axs[0,1]; ax.set_title('Scatter+line: X, Y, Y-error') 
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
    if n%2==0 and n+2<len(ys):  # datasets read in pairs; 2nd in pair used as Y-errorbars
        ax.plot(x, y, label="%s" % (label), color=color, linewidth=0, marker='od^sph'[n%6])
        #ax.errorbar(x, ys[n], yerr=ys[n+1], label="%s" % (label), color=color, capsize=5)
        ax.errorbar(x, ys[n], label="%s" % (label), color=color, capsize=5,
                yerr=np.vstack((ys[n+1]*0.04, ys[n+1]*0.08)), 
                xerr=np.vstack((ys[n+1]*0.02, ys[n+1]*0.01)))

ax = axs[0,2]; ax.set_title('Scatter+line: X, Y, size, color') 
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
    if n%3==0 and n+3<len(ys):  
        # datasets read in triplets; 2nd in triplet encodes size, 3rd in triplet encodes colour
        ax.plot(x, ys[n], c='black', lw=.5) ## thin black connecting line
        ax.scatter(x, ys[n], s=ys[n+1], c=ys[n+2], label="%s" % (label), edgecolors='black')

ax = axs[0,3]; ax.set_title('Line + uncertainty area') 
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
    if n%2==0 and n+2<=len(ys):  
        ax.plot(x, ys[n], color=color)  ## filled semi-transparent area 
        ax.fill_between(x, ys[n]-ys[n+1], ys[n]+ys[n+1], color=color, alpha=0.2)  ## filled semi-transparent area 



    #           horizontal bar plot         stacked bar                        radar plot                         nested pie plot
ax = axs[1,0]; ax.set_title('Grouped bars (X values unused)') 
width = 0.8/len(xs)    ## auto width to fit all bars next to each other
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
    ax.bar(np.arange(len(x))+width*n, y, width=width, color=color, align='center')

ax = axs[1,1]; ax.set_title('Stacked bars (X values unused)') 
width, relshift = 0.8, 0    ## column full width (and optionally lateral shift to show, e.g., negative values)
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
     ax.bar(np.arange(len(x)), ys[n], bottom=np.sum(ys[:n],axis=0), width=width, color=color, align='center')

ax = axs[1,2]; ax.set_title('Stacked lines') 
width, relshift = 0.8, 0    ## column full width (and optionally lateral shift to show, e.g., negative values)
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
     #ax.fill_between(x, ys[n], ys[n+1], color=color, alpha=0.3)  ## filled semi-transparent area 
     ax.fill_between(x, np.sum(ys[:n],axis=0), np.sum(ys[:n+1],axis=0), color=color)


ax = axs[1,3]; ax.set_title('Concentric pie plot') 
## Note: for more examples, see https://matplotlib.org/3.2.0/gallery/index.html#pie-and-polar-charts 
## and https://matplotlib.org/3.2.0/gallery/pie_and_polar_charts/nested_pie.html#sphx-glr-gallery-pie-and-polar-charts-nested-pie-py
ax.set_aspect(1.0, anchor='C') 
rel_thickness, rel_min_radius = 0.8, 0.3
for n, y_col in enumerate(np.array(ys).T):   ## note this cycles through "columns" in y, not "rows" as usual
    ax.pie(y_col[~np.isnan(y_col)], radius=1-(1-rel_min_radius)*n/len(ys[0]), 
            colors=colors, wedgeprops=dict(width=.8/len(ys[0]), edgecolor='white', label=labels if n==0 else None) )
ax.legend()




ax = axs[2,0]; ax.set_title('2D contours') 
ys = np.array(ys)
cmaprange1, cmaprange2 = np.min(ys), np.max(ys) 
levels = np.linspace(cmaprange1, cmaprange2, 50) 

## Example generated parameters  (comment out if file header/name provides valid params)
param = np.linspace(10, 20, len(xs)) 

DATA_GRIDDED = True # todo - check if xs[0]==xs[1]==.. and so on, also for param
if DATA_GRIDDED:
    ax.contour(xs[0], param, ys, levels=levels)
    ax.contourf(xs[0], param, ys, levels=levels)
else:
    # Prepare param array for each data point (so far each file had one item in params)
    paramss = np.array(list(p*np.ones_like(x) for p,x in  zip(params, xs))) 
    ax.tricontourf(np.array(xs).flatten(), np.array(paramss).flatten(), np.array(ys).flatten(), levels=levels, extend='both')



# alternatively put here: 2D contour plot log(ys)
ax = axs[2,1]; ax.set_title('Isotropic image pixels') 
ax.imshow(ys)

ax = axs[2,2]; ax.set_title('Waterfall plot') 
for          x,  y,  param,  label,  color,  n,         in \
         zip(xs, ys, params, labels, colors, range(len(xs))):
    vspace = np.max(ys[~np.isnan(ys)])*2/len(xs)
    ax.plot(x,y+n*vspace,marker='.',c='k',lw=.5)
    ax.fill_between(x, n*vspace, y+n*vspace, color=color, alpha=.3)




## Axes projection cannot be changed at runtime; but a new object can be made
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
axs[2,3].remove(); ax = fig.add_subplot(3, 4, 12, projection='3d') ; ax.set_title('3D surface') 

param = np.linspace(10, 20, len(xs)) 
X, P = np.meshgrid(xs[0], param)

# Plot the surface.
surf = ax.plot_surface(X, P, np.array(ys/100), cmap=cm.viridis, linewidth=0, antialiased=False)
#cset = ax.contour(X, P, np.array(ys/100), color='k')
ax.plot_wireframe(X, P, np.array(ys/100), rstride=1, cstride=1, color='k', lw=.5)

# Customize the z axis.
#ax.set_zlim(-1.01, 1.01)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))


    #           2D contour plot                       waterfall plot                      3D surface
#ax.set_xlabel(xlabelsdedup)
#ax.set_ylabel(ylabelsdedup[:20])
    # x, y = x[~np.isnan~np.isnan(y)]        ## filter-out NaN points
    # convol = 2**-np.linspace(-2,2,25)**2; y = np.convolve(y,convol/np.sum(convol), mode='same') ## simple smoothing


