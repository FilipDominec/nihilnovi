ax3 = ax.twiny()  # SECONDARY HORIZONTAL AXIS on the top
def top_tick_function(p): 
    return p**2   # arbitrary user selected function
ax3.set_xlim(np.array(ax.get_xlim()))      
ax3.set_xlabel('squared values from X-axis')
## If we force nice round numbers on the secondary axis ticks...
top_ax_limits = sorted([top_tick_function(lim) for lim in ax.get_xlim()])
xticks2 = matplotlib.ticker.MaxNLocator(nbins=8, steps=[1,2,5]).tick_values(*top_ax_limits)
## ... we must explicitly find their positions. To do so, we need to numerically invert the tick values:
from scipy.optimize import brentq
def top_tick_function_inv(r, target_value=0): 
    return brentq(lambda r,q: top_tick_function(r) - target_value, ax.get_xlim()[0], ax.get_xlim()[1], 1e6)
valid_xtick2loc, valid_xtick2val = [], []
for xtick2 in xticks2:
    try:
        valid_xtick2loc.append(top_tick_function_inv(0, xtick2))
        valid_xtick2val.append(xtick2)
    except ValueError:      ## (skip tick if the ticker.MaxNLocator gave invalid target_value to brentq optimization)
        pass
ax3.set_xticks(valid_xtick2loc)     ## Finally, we set the positions
from matplotlib.ticker import FixedFormatter ## ... and tick values
ax3.xaxis.set_major_formatter(FixedFormatter(["%g" % toptick for toptick in valid_xtick2val]))

