
def onclick(event):
    print('Clicked at coordinates x,y = {event.xydata} with button {event.button}')
cid = fig.canvas.mpl_connect('button_press_event', onclick)
