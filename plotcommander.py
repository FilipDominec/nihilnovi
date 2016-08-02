#!/usr/bin/python3
#-*- coding: utf-8 -*-

import gi, sys, os
import numpy as np
#import FDMeasurementRecords
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

## Plotting dependencies and settings
from gi.repository import Gtk
import matplotlib
#from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas   # .. backend is broken currently
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo  as FigureCanvas
from matplotlib.backends.backend_gtk3      import NavigationToolbar2GTK3 as NavigationToolbar

## TODO These settings should be loaded dynamically from ./plotcommanderrc.py, ../plotcommanderrc.py, ../../plotcommanderrc.py, ...
matplotlib.rcParams['font.family'] = 'serif'        
matplotlib.rcParams['font.size'] = 9
matplotlib.rcParams['axes.linewidth'] = .5
matplotlib.rcParams['savefig.facecolor'] = "white"

class Handler:
    ## == initialization == 
    def __init__(self, builder): #{{{
        self.builder = builder

        fig = matplotlib.figure.Figure(figsize=(8,8), dpi=96, facecolor='#eeeeee', tight_layout=1)
        ax = fig.add_subplot(111) 

        for infile in sys.argv[1:]: 
            print("\n\nLoading file: %s" % infile)
            try: 
                ## Add the treeview item in the left panel
                if 'oldtr' in locals(): oldertr = oldtr
                oldtr = w('treestore1').append(None, ['no', infile])
                if 'oldertr' in locals(): oldtr.parent = oldertr
                # TODO - use icons?
                #w('treestore1').append(None, ['no', Gtk.IconTheme.get_default().load_icon('edit-cut', 16, 0), infile])
                # TODO - moving rows http://www.pygtk.org/pygtk2tutorial/sec-TreeModelInterface.html

                # TODO - on window resize, adjust borders? 
                # http://stackoverflow.com/questions/6066091/python-matplotlib-figure-borders-in-wxpython

                ## Plot the curve in the right panel
                x, y = np.genfromtxt(infile, usecols=[0,1], unpack=True,  dtype=type(0.0), 
                        comments='#', delimiter=None, skip_header=0, skip_footer=0,           ## default options follow...
                        converters=None, missing_values=None, filling_values=None, names=None, excludelist=None, 
                        deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', 
                        usemask=False, loose=True, invalid_raise=True) 
                # , max_rows=None ## does not work with older numpy?
                ax.plot(x, y, label=os.path.basename(infile))
            except ValueError as e:
                print(type(e).__name__ + ": " + str(e))

        ax.legend(loc="upper right")
        ax.grid(True)

        canvas = FigureCanvas(fig)
        canvas.set_size_request(300,300)
        toolbar = matplotlib.backends.backend_gtk3.NavigationToolbar2GTK3(canvas, w('box4').get_parent_window())
        sw = Gtk.ScrolledWindow()
        sw.add_with_viewport(canvas)
        w('box4').pack_start(toolbar, False, True, 0)
        w('box4').pack_start(sw, True, True, 0)

        toolbar.pan() #todo - define global shortcuts as a superset of the Matplotlib-GUI's internal, include also:
        #toolbar.zoom() #toolbar.home() #toolbar.back() #toolbar.forward() #toolbar.save_figure(toolbar)

        from matplotlib.widgets import Cursor
        cursor = Cursor(ax, useblit=True, color='red', linewidth=2)
        #}}}

    ## == trivial GUI handlers ==
    def on_window1_delete_event(self, *args):# {{{
        Gtk.main_quit(*args)# }}}



builder = Gtk.Builder()
builder.add_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "plotcommander.glade"))
def w(widgetname): return builder.get_object(widgetname)   # shortcut to access widgets 
builder.connect_signals(Handler(builder))

window = builder.get_object("window1")
window.maximize()
window.show_all()

Gtk.main()
