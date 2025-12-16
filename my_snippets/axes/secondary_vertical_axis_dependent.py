ax2 = ax.twinx()  # SECONDARY VERTICAL AXIS on the right
def right_tick_function(p): 
    return p**2      # arbitrary user selected function
ax2.set_ylabel('squared values from Y-axis')
ax2.set_ylim(np.array(ax.get_ylim()))
## If we force nice round numbers on the secondary axis ticks...
right_ax_limits = sorted([right_tick_function(lim) for lim in ax.get_ylim()])
yticks2 = matplotlib.ticker.MaxNLocator(nbins=8, steps=[1,2,5]).tick_values(*right_ax_limits)
## ... we must explicitly find their positions. To do so, we need to numerically invert the tick values:
from scipy.optimize import brentq
def right_tick_function_inv(r, target_value=0):
    return brentq(lambda r,q: right_tick_function(r) - target_value, ax.get_ylim()[0], ax.get_ylim()[1], 1e6)
valid_ytick2loc, valid_ytick2val = [], []
for ytick2 in yticks2:
    try:
        valid_ytick2loc.append(right_tick_function_inv(0, ytick2))
        valid_ytick2val.append(ytick2)
    except ValueError:      ## (skip tick if the ticker.MaxNLocator gave invalid target_value to brentq optimization)
        pass
ax2.set_yticks(valid_ytick2loc)     ## Finally, we set the positions 
from matplotlib.ticker import FixedFormatter ## ... and tick values
ax2.yaxis.set_major_formatter(FixedFormatter(["%g" % righttick for righttick in valid_ytick2val]))

