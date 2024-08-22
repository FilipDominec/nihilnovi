# Creates two additional thin plots adjacent to the main plot, as shown in 
# https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html
fig.delaxes(ax)
gs = fig.add_gridspec(2, 2,  width_ratios=(4, 1), height_ratios=(1, 4))
              #left=0.01, right=0.99, bottom=0.1, top=0.9, #wspace=0.05, hspace=0.05)

# In the following, use these three axes objects as you need
ax = fig.add_subplot(gs[1, 0])
ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)
