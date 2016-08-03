#!/usr/bin/python3
#-*- coding: utf-8 -*-

import gi, sys, os, signal
import numpy as np

## Plotting dependencies and settings
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import matplotlib
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo  as FigureCanvas # "..Agg" backend is broken currently
from matplotlib.backends.backend_gtk3      import NavigationToolbar2GTK3 as NavigationToolbar


## TODO These settings should be loaded dynamically from ./plotcommanderrc.py, ../plotcommanderrc.py, ../../plotcommanderrc.py, ...
matplotlib.rcParams['font.family'] = 'serif'        
matplotlib.rcParams['font.size'] = 9
matplotlib.rcParams['axes.linewidth'] = .5
matplotlib.rcParams['savefig.facecolor'] = "white"
#import FDMeasurementRecords

class Handler:
    ## == initialization == 
    def __init__(self): #{{{
        ## Init the table of records (i.e. files or similar datasets)
        self.record_labels = {}
        self.record__types = {}

        ## Plotting initialization
        self.fig = matplotlib.figure.Figure(figsize=(8,8), dpi=96, facecolor='#eeeeee', tight_layout=1)
        self.ax = self.fig.add_subplot(111) 
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(300,300)
        self.toolbar = matplotlib.backends.backend_gtk3.NavigationToolbar2GTK3(self.canvas, w('box4').get_parent_window())
        self.sw = Gtk.ScrolledWindow()
        self.sw.add_with_viewport(self.canvas)
        w('box4').pack_start(self.toolbar, False, True, 0)
        #self.toolbar.append_item(Gtk.Button('tetet')) ## TODO find out how to modify the NavigationToolbar...
        w('box4').pack_start(self.sw, True, True, 0)
        self.toolbar.pan() #todo - define global shortcuts as a superset of the Matplotlib-GUI's internal, include also:
        #toolbar.zoom() #toolbar.home() #toolbar.back() #toolbar.forward() #toolbar.save_figure(toolbar)
        
        ## TreeStore and ListStore initialization

        ## Load records (if provided as arguments at startup)
        for infile in sys.argv[1:]: 
            self.add_record(infile, tree_parent=None) ## TODO use dir hierarchy

        ## Select all input files at start, and plot them
        #TODO:set all argv[:] 
        self.plot_reset()
        self.plot_all_sel_records()


        ## Add the data cursor by default  # TODO - make this work
        from matplotlib.widgets import Cursor
        cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        #}}}

    ## === DATA HANDLING ===
    def add_record(self, file_path, tree_parent=None):
        ## Add the treeview item in the left panel
        new_trs_item = w('treestore1').append(tree_parent, ['no', file_path])

        ## Register a new record in the record table
        self.record_labels[file_path] = os.path.basename(file_path) 
        self.record__types[file_path] = 'file'

    ## === FILE HANDLING ===
    

    ## === GRAPHICAL PRESENTATION ===
    def plot_reset(self):
        self.ax.cla() ## TODO clearing matplotlib plot - this is inefficient, rewrite
        self.ax.legend(loc="upper right")
        self.ax.grid(True)

    def plot_all_sel_records(self):
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        for path in pathlist:
            file_name = w('treestore1').get_value(w('treestore1').get_iter(path), 1)
            print(file_name)
            self.plot_record(file_name)

    def plot_record(self, infile):
        ## Plotting "on-the-fly", i.e., program does not store any data and loads them from disk upon every (re)plot
        x, y = np.genfromtxt(infile, usecols=[0,1], unpack=True,  dtype=type(0.0), 
                comments='#', delimiter=None, skip_header=0, skip_footer=0,           ## default options follow...
                converters=None, missing_values=None, filling_values=None, names=None, excludelist=None, 
                deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', 
                usemask=False, loose=True, invalid_raise=True) # , max_rows=None ## does not work with older numpy?
                # TODO apply file loading options

        ## Plot the curve in the right panel
        self.ax.plot(x, y, label=os.path.basename(infile)) # TODO apply plotting options
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    ## == USER INTERFACE HANDLERS ==
    def on_window1_delete_event(self, *args):# {{{
        Gtk.main_quit(*args)# }}}

    def on_treeview1_selection_changed(self, *args):
        
        self.plot_reset()               ## first delete the curves, to hide (also) unselected plots
        self.plot_all_sel_records()     ## then show the selected ones


signal.signal(signal.SIGINT, signal.SIG_DFL)
builder = Gtk.Builder()
builder.add_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "plotcommander.glade"))
def w(widgetname): return builder.get_object(widgetname)   # shortcut to access widgets 
builder.connect_signals(Handler())

window = builder.get_object("window1")
window.maximize()
window.show_all()

Gtk.main()



            # TODO - use icons?
            #w('treestore1').append(None, ['no', Gtk.IconTheme.get_default().load_icon('edit-cut', 16, 0), infile])
            # TODO - moving rows http://www.pygtk.org/pygtk2tutorial/sec-TreeModelInterface.html

            # TODO - on window resize, adjust borders? 
            # http://stackoverflow.com/questions/6066091/python-matplotlib-figure-borders-in-wxpython
