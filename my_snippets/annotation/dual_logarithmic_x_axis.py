## dual axis for the x-axes (relation between photon energy and wavelength)
def top_tick_function(p): return 1e6*(np.pi*2)/p
ax3 = ax.twiny()
ax3.set_xscale('log') ## LOG!
#ax2.axis['top'].major_ticklabels.set_visible(False)
ax3.set_xlim(np.array(ax.get_xlim()))
ax3.set_xlabel('characteristic feature size (μm)')

## If we wish nice round numbers on the secondary axis ticks...
## ... we must give them correct positions. To do so, we need to numerically invert the tick values:
top_ax_limits = ([top_tick_function(lim) for lim in ax.get_xlim()])
xticks2 = 10**(matplotlib.ticker.MaxNLocator(nbins=8, steps=[1]).tick_values(np.log10(top_ax_limits[1]), np.log10(top_ax_limits[0])))
from scipy.optimize import brentq
def top_tick_function_inv(r, target_value=0): 
    return (brentq(lambda r,q: top_tick_function(r) - target_value, ax.get_xlim()[1], ax.get_xlim()[0], 1e-6))
valid_xtick2loc, valid_xtick2val = [], []
for xtick2 in xticks2:
    try:
        valid_xtick2loc.append(top_tick_function_inv(0, xtick2))
        valid_xtick2val.append(xtick2)
    except ValueError:      ## (skip tick if the ticker.MaxNLocator gave invalid target_value to brentq optimization)
        pass
## Finally, we set the positions and tick values
print("valid_xtick2loc",valid_xtick2loc,"valid_xtick2val", valid_xtick2val)
ax3.set_xticks(valid_xtick2loc)
from matplotlib.ticker import FixedFormatter, NullFormatter
ax3.xaxis.set_major_formatter(FixedFormatter(["%g" % toptick for toptick in valid_xtick2val]))
ax3.set_minor_formatter(NullFormatter())
