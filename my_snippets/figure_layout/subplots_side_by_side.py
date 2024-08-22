fig.delaxes(ax)
axs = fig.subplots(nrows=1, ncols=2, sharex=False, sharey=False)
ax = axs[0] # anytime, you may switch to other subplots in a similar way 
#axs = [ax for axx in axs for ax in axx]  ## optionally flatten
