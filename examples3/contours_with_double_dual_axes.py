


ys = np.array(ys)
cmaprange1, cmaprange2 = np.min(ys), np.max(ys) 
levels = 10**(np.linspace(np.log10(cmaprange1), np.log10(cmaprange2), 20)) 
x = sc.h*sc.c/sc.nano/xs[0]/sc.e
p = np.hstack([np.arange(2, 4.6, 0.5), np.arange(5, 9.1, 1.0)])

CS=contours = ax.contourf(x, p, ys, levels=levels, extend='both', cmap='gist_earth_r')
contours = ax.contour(x, p, ys, levels=levels, extend='both', cmap='gist_earth_r')
matplotlib.colorbar.Colorbar(ax, mappable=CS)
ax.set_xlabel('optical energy (eV)')
ax.set_ylabel('electron energy (keV)')

ax.set_title('cathodoluminescence of sample "029" (20xQW) \n\n\n')
ax.set_xlim([1.6,3.5])

ax2 = ax.twinx()
def tick_function(r): 
    return 10.46*(r**1.68)
def tick_function_inv(r): 
    return (r/10.46)**(1/1.68)
print (tick_function)
print (tick_function(30))
print ([tick_function(yyy) for yyy in range(10)])

## Step 1: Let us Matplotlib decide what the right-axis tick values would be
ylim = ax.get_ylim()
print (tick_function)
print (tick_function(ylim[1]))
print ([tick_function(lim) for lim in ylim])
ax2.set_ylim([tick_function(lim) for lim in ylim])
yticks2=ax2.get_yticks() 

## Step 2: Compute their corresponding positions on the left y-axis (i.e. invert the user function)
label_pos_legend = [(tick_function_inv(ytick2), ytick2) for ytick2 
        in yticks2 if not np.isnan(tick_function_inv(ytick2))]
pos, legend = zip(*label_pos_legend[:-1])  ## last value left out, since it shifted the upper ax2 limit

## Step 3: Set the same limits on right y-axis as are on the left one
ax2.set_ylim(ylim)
ax2.set_yticks(pos)
ax2.set_yticklabels(legend)
ax2.set_ylabel('electron penetration depth (nm)')


ax3 = ax.twiny()
def tick_function(r): 
    return sc.c*sc.h/r/sc.e/sc.nano
def tick_function_inv(r): 
    return sc.c*sc.h/r/sc.e/sc.nano



## Step 1: Let us Matplotlib decide yhat the right-ayis tick values yould be
xlim = ax.get_xlim()
print (tick_function)
print (tick_function(xlim[1]))
print ([tick_function(lim) for lim in xlim])
ax3.set_xlim([tick_function(lim) for lim in xlim])
xticks2=ax3.get_xticks() 

## Step 2: Compute their corresponding positions on the left x-ayis (i.e. invert the user function)
label_pos_legend = [(tick_function_inv(xtick2), xtick2) for xtick2 
        in xticks2 if not np.isnan(tick_function_inv(xtick2))]
pos, legend = zip(*label_pos_legend[:-1])  ## last value left out, since it shifted the upper ax3 limit

## Step 3: Set the same limits on right x-ayis as are on the left one
ax3.set_xlim(xlim)
ax3.set_xticks(pos)
ax3.set_xticklabels(legend)
ax3.set_xlabel('optical wavelength (nm)')


del(ax3)
del(ax2)
