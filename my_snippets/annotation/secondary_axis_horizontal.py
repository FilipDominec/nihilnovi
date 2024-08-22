
ax_right = ax.twinx()
# now you can independently use ax_right.plot() etc. to get independent, but overlapping graphs as usual in papers

## Grouping the lines/datapoints can be elegantly done with unicode 
## symbols:    21a9 ↩   and    21aa ↪     (or 21b2, 21b3 are larger alternatives)
ax.text('↩', size=30)
ax_right.text('↪', size=30)
# TODO!


