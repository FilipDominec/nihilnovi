for t,x in zip(
    ['C',    'N',    'O',    'Ni',    'Ga',    'Si',   'Pt',   'Au',   'Pd',   'Ag',  'In',  'Sn',   'Ti',   'Ni'],
    [.28,    .39,    .525,   .849,    1.098,    1.740, 2.05,   2.123,  2.838,  2.983, 3.286, 3.444,  4.512,  7.48]
    ):
    #print(np.interp(x,xs[-1]/100, ys[-1]), xs[-1],ys[-1])
    #ax.text(x=x,y=np.interp(x,xs[-1]/100,ys[-1]),s=t,ha='center')
    ax.text(x=x,y=np.interp(x,xs[-1]/100,ys[-1])*10**n*1.5,s=t,ha='center', weight='bold')
    ax.axvspan(xmin=x-.05, xmax=x+0.05,fc='k' if t!='In' else 'r',alpha=.2)
