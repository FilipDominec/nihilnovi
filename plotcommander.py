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
        self.record_titems = {}
        self.record_labels = {}
        self.record_curves = {}
        self.record__types = {}

        ## Load records (if provided as arguments at startup)
        for infile in sys.argv[1:]: 
            self.add_record(infile, tree_parent=None) ## TODO use dir hierarchy

        ## Select all input files at start, and plot them
        #TODO:set all argv[:] 
        self.plot_all_sel_records()

        ## Plotting initialization
        fig = matplotlib.figure.Figure(figsize=(8,8), dpi=96, facecolor='#eeeeee', tight_layout=1)
        ax = fig.add_subplot(111) 
        ax.legend(loc="upper right")
        ax.grid(True)
        canvas = FigureCanvas(fig)
        canvas.set_size_request(300,300)
        toolbar = matplotlib.backends.backend_gtk3.NavigationToolbar2GTK3(canvas, w('box4').get_parent_window())
        sw = Gtk.ScrolledWindow()
        sw.add_with_viewport(canvas)
        w('box4').pack_start(toolbar, False, True, 0)
        #toolbar.append_item(Gtk.Button('tetet')) ## TODO find out how to modify the NavigationToolbar...
        w('box4').pack_start(sw, True, True, 0)
        toolbar.pan() #todo - define global shortcuts as a superset of the Matplotlib-GUI's internal, include also:
        #toolbar.zoom() #toolbar.home() #toolbar.back() #toolbar.forward() #toolbar.save_figure(toolbar)

        ## Add the data cursor by default  # TODO - make this work
        from matplotlib.widgets import Cursor
        cursor = Cursor(ax, useblit=True, color='red', linewidth=2)

        #}}}

    ## === DATA HANDLING ===
    def add_record(self, file_path, tree_parent=None):
        ## Add the treeview item in the left panel
        new_trs_item = w('treestore1').append(tree_parent, ['no', file_path])

        ## Plot it
        new_curve = None # FIXME

        ## Register a new record in the record table
        self.record_titems[file_path] = new_trs_item
        self.record_labels[file_path] = os.path.basename(file_path) 
        self.record_curves[file_path] = new_curve
        self.record__types[file_path] = 'file'


    ## === GRAPHICAL PRESENTATION ===
    def treepath_to_filepath(self, treepath):
        """ reverse search in dictionary, when its values (i.e. <treeiter> type) are not hashable """
        for item in self.record_titems.items():
            print(item[1] , treepath, item[1] is treepath)
        print([item[0] for item in self.record_titems.items()  if  item[1] is treepath])
        print([item[0] for item in self.record_titems.items()  if  item[1] is treepath][0])
        return [item[0] for item in self.record_titems.items()  if  item[1] is treepath][0]

    def plot_all_sel_records(self):
        model, sel_tree_paths = w('treeview1').get_selection().get_selected_rows()
        for sel_tree_path in sel_tree_paths:
            sel_file_path = self.treepath_to_filepath(sel_tree_path)
            print('FILEPATH     = ', sel_file_path)
            print(' ----> label = ', self.record_labels[sel_file_path])

            #try: 
            #except ValueError as e:
                #print(type(e).__name__ + ": " + str(e))
        #print("sel_tree_path", dir(sel_tree_path))
        #print([record for record in self.records if (record.treerowref.get_path() in sel_tree_paths)])
        #print("sel_tree_paths", sel_tree_paths)
        #sps = [sp for sp in sel_tree_paths]
        #print("sel_tree_paths-bis", sps)
        #print("REPLOTTING", len(sel_tree_paths))

    def plot_record(self, trs_item):
        ## Plotting "on-the-fly", i.e., program does not store any data and loads them from disk upon every (re)plot
        print("\n\nLoading file: %s" % self.record_fpaths[trs_item])
           #x, y = np.genfromtxt(infile, usecols=[0,1], unpack=True,  dtype=type(0.0), 
           #        comments='#', delimiter=None, skip_header=0, skip_footer=0,           ## default options follow...
           #        converters=None, missing_values=None, filling_values=None, names=None, excludelist=None, 
           #        deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', 
           #        usemask=False, loose=True, invalid_raise=True) # , max_rows=None ## does not work with older numpy?

           ### Plot the curve in the right panel
           #ax.plot(x, y, label=os.path.basename(infile))

    ## == user interface handlers ==
    def on_window1_delete_event(self, *args):# {{{
        Gtk.main_quit(*args)# }}}

    def on_treeview1_selection_changed(self, *args):
        ## TODO ... first delete the curves for unselected plots
        self.plot_all_sel_records() 


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
