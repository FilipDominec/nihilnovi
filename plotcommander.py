#!/usr/bin/python3
#-*- coding: utf-8 -*-

import gi, sys, os, signal, stat, traceback
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
        self.toolbar.pan() 
        #TODO - define global shortcuts as a superset of the Matplotlib-GUI's internal, include also:
        #toolbar.zoom() #toolbar.home() #toolbar.back() #toolbar.forward() #toolbar.save_figure(toolbar)
        #TODO http://stackoverflow.com/questions/26433169/personalize-matplotlib-toolbar-with-log-feature


        ## TreeStore and ListStore initialization
        from gi.repository.GdkPixbuf import Pixbuf
        self.treestore1 = Gtk.TreeStore(str, Pixbuf, str)       # initialize the filesystem treestore
        treeViewCol0 = Gtk.TreeViewColumn("Plot")        # Create a TreeViewColumn
        treeViewCol = Gtk.TreeViewColumn("File")        # Create a TreeViewColumn
        colCellText = Gtk.CellRendererText()        # Create a column cell to display text
        colCellImg = Gtk.CellRendererPixbuf()       # Create a column cell to display an image
        treeViewCol.pack_start(colCellImg, expand=False)       # Add the cells to the column
        treeViewCol.pack_start(colCellText, expand=True)
        treeViewCol.add_attribute(colCellImg, "pixbuf", 1)      # Bind the image cell to column 1 of the tree's model
        treeViewCol.add_attribute(colCellText, "text", 2)       # Bind the text cell to column 0 of the tree's model
        w('treeview1').append_column(treeViewCol)       # Append the columns to the TreeView
        w('treeview1').set_model(self.treestore1)       # Append the columns to the TreeView
        w('treeview1').set_enable_tree_lines(True) 
        w('treeview1').connect("row-expanded", self.onRowExpanded)       # add "on expand" callback
        w('treeview1').connect("row-collapsed", self.onRowCollapsed)         # add "on collapse" callback
        itemIcon = Gtk.IconTheme.get_default().load_icon("folder", 8, 0) # Generate a default icon TODO
        w('treeview1').append_column(treeViewCol0)       # Append the columns to the TreeView
        colCellText0 = Gtk.CellRendererText()        # Create a column cell to display text
        treeViewCol0.pack_start(colCellText0, expand=False)
        colCellText0 = Gtk.CellRendererText()        # Create a column cell to display text
        treeViewCol0.add_attribute(colCellText0, "text", 0)      # Bind the image cell to column 1 of the tree's model



        ## Select all input files at start, and plot them
        if len(sys.argv) > 1:    self.populateFileSystemTreeStore(self.treestore1, sys.argv[1], parent=None) ## TODO 
        else:                    self.populateFileSystemTreeStore(self.treestore1, os.path.dirname(os.getcwd()), parent=None) ## TODO 
        self.plot_reset()
        self.plot_all_sel_records()


        ## Add the data cursor by default  # TODO - make this work
        from matplotlib.widgets import Cursor
        cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        #}}}


    ## === DATA HANDLING ===
    def add_record(self, file_path, tree_parent=None):
        ## Add the treeview item in the left panel

        #itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "empty", 8, 0) # Generate a default icon

        ## Register a new record in the record table
        self.record_labels[file_path] = os.path.basename(file_path) 
        self.record__types[file_path] = 'file'

    ## === FILE HANDLING ===
    def populateFileSystemTreeStore(self, treeStore, path, parent=None):
        itemCounter = 0
        listdir = os.listdir(path)
        listdir.sort()
        for item in listdir:                           # iterate over the items in the path
            itemFullname = os.path.join(path, item)             # Get the absolute path of the item
            itemMetaData = os.stat(itemFullname) # Extract metadata from the item
            itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
            if itemIsFolder:
                icon = 'folder' # Determine if the item is a folder
            elif item[-4:] == '.dat':
                icon = 'empty'   ## if can not load, change icon to stock_dialog-warning
            else:
                icon = 'gtk-stop' 
            itemIcon = Gtk.IconTheme.get_default().load_icon(icon, 8, 0) # Generate a default icon
            currentIter = treeStore.append(parent, [itemFullname, itemIcon, item])      # Append the item to the TreeStore
            if itemIsFolder: treeStore.append(currentIter, [None, None, None])      # add dummy if current item was a folder
            itemCounter += 1                                    #increment the item counter
        if itemCounter < 1: treeStore.append(parent, [None, None, None])        # add the dummy node back if nothing was inserted before

    def onRowExpanded(self, treeView, treeIter, treePath):
        treeStore = treeView.get_model()        # get the associated model
        newPath = treeStore.get_value(treeIter, 0)      # get the full path of the position
        self.populateFileSystemTreeStore(treeStore, newPath, treeIter)       # populate the subtree on curent position
        treeStore.remove(treeStore.iter_children(treeIter))         # remove the first child (dummy node)

    def onRowCollapsed(self, treeView, treeIter, treePath):
        treeStore = treeView.get_model()        # get the associated model
        currentChildIter = treeStore.iter_children(treeIter)        # get the iterator of the first child
        while currentChildIter:         # loop as long as some childern exist
            treeStore.remove(currentChildIter)      # remove the first child
            currentChildIter = treeStore.iter_children(treeIter)        # refresh the iterator of the next child
        treeStore.append(treeIter, [None, None, None])      # append dummy node
    

    ## === GRAPHICAL PRESENTATION ===
    def plot_reset(self):
        self.ax.cla() ## TODO clearing matplotlib plot - this is inefficient, rewrite

    def plot_all_sel_records(self):
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        for path in pathlist:
            try:
                file_name = self.treestore1.get_value(self.treestore1.get_iter(path), 0)
                self.plot_record(file_name)
            except ValueError:
                traceback.print_exc()
        self.ax.legend(loc="upper right")
        self.ax.grid(True)

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

    ## == USER INTERFACE HANDLERS ==
    def on_window1_delete_event(self, *args):# {{{
        Gtk.main_quit(*args)# }}}

    def on_treeview1_selection_changed(self, *args):
        self.plot_reset()               ## first delete the curves, to hide (also) unselected plots
        self.plot_all_sel_records()     ## then show the selected ones
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


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
