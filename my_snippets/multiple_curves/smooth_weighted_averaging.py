# compute smooth weighted average of all selected curves
AVERAGE_POINTS = 1000      # resulting curve resolution
XLOG, YLOG = False, False   # affects the averaging weights if data are to be shown in log plots
if XLOG: xs = [np.log10(x) for x in xs]
if YLOG: ys = [np.log10(y) for y in ys]
minx, maxx = np.min([np.min(x) for x in xs]), np.max([np.max(x) for x in xs])
wxs, wys, wws = np.linspace(minx,maxx, AVERAGE_POINTS), np.zeros(AVERAGE_POINTS), np.zeros(AVERAGE_POINTS)
for (x,y) in zip(xs,ys):    
    centerx,extx = np.min(x)/2+np.max(x)/2, np.max(x)/2-np.min(x)/2
    weight = np.exp(-((wxs-centerx)*1.3/extx)**4)
    weight[np.logical_or(wxs<np.min(x),wxs>np.max(x))] = 0
    if XLOG: weight *= np.exp(((wxs-centerx)*1/extx)) # optional: more weight on right side of function
    ax.plot(10**wxs, weight)
    wys += np.interp(wxs,x,y) * weight
    wws += weight
if XLOG: xs = [10**(x) for x in xs]
if YLOG: ys = [10**(y) for y in ys]
resulting_x, resulting_y = 10**wxs if XLOG else wxs, 10**(wys/wws) if YLOG else (wys/wws)
ax.plot(resulting_x, resulting_y, color='k', lw=1.5)
