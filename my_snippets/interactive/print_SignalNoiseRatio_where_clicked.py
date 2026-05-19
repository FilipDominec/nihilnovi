

def onclick(event):
    #print(f'The Click Event Triggered! {event.button=} {(event.ydata, event.xdata)}')
    if event.button==1:
        ns = image[int(event.ydata)-40:int(event.ydata)+40,
                   int(event.xdata)-20:int(event.xdata)+20]  # vertical rectangle for noise sample: tube
        # Image may be inhomogeneous; therefore taking SNR from a difference between close pixels may
        # give higher values, which better represent the pixel-wise Poissonian "shot" noise. 
        # When subtracting/adding two noisy pixels, is fair to multiply SNR result by square root of two.    
        print('averaged SNR in tube 80x40px absolute        ', basename, np.mean(ns) / np.std(ns) )
        print('                     80x40px differential4pxV', basename, np.mean(ns) / np.std((ns-np.roll(ns,4,axis=0))[4:-4,4:-4]) * 2**.5)
        print('                     80x40px differential4pxV', basename, np.mean(ns) / np.std((ns-np.roll(ns,4,axis=1))[4:-4,4:-4]) * 2**.5 )
cid = fig.canvas.mpl_connect('button_press_event', onclick)

