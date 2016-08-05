#!/usr/bin/python3
#-*- coding: utf-8 -*-

import gi, sys, os, signal, stat, traceback
import numpy as np

## Plotting dependencies and settings
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf,Colorspace

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
        np.seterr(all='ignore')

        ## Plotting initialization
        self.fig = matplotlib.figure.Figure(figsize=(8,8), dpi=96, facecolor='#eeeeee', tight_layout=1)
        self.ax = self.fig.add_subplot(111) 
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(300,300)
        self.toolbar = matplotlib.backends.backend_gtk3.NavigationToolbar2GTK3(self.canvas, w('box4').get_parent_window())
        self.sw = Gtk.ScrolledWindow()
        self.sw.add_with_viewport(self.canvas)
        w('box4').pack_start(self.toolbar, False, True, 0)
        #self.toolbar.append_item(Gtk.Button('tetet')) 
        ## TODO find out how to modify the NavigationToolbar...
        w('box4').pack_start(self.sw, True, True, 0)
        self.toolbar.pan() 
        #TODO - define global shortcuts as a superset of the Matplotlib-GUI's internal, include also:
        #toolbar.zoom() #toolbar.home() #toolbar.back() #toolbar.forward() #toolbar.save_figure(toolbar)
        #TODO http://stackoverflow.com/questions/26433169/personalize-matplotlib-toolbar-with-log-feature
        #TODO http://dalelane.co.uk/blog/?p=778


        ## TreeStore and ListStore initialization
        self.treestore1 = Gtk.TreeStore(str,        Pixbuf, str,        Pixbuf        )
        ## column meaning:              0:filepath  1:icon  2:name      3:plotstyleicon
        self.dummy_treestore_row = [None, None, None, None]

        treeViewCol0 = Gtk.TreeViewColumn("Plot")        # Create a TreeViewColumn
        colCellPlot = Gtk.CellRendererPixbuf()        # Create a column cell to display text
        treeViewCol0.pack_start(colCellPlot, expand=True)
        treeViewCol0.add_attribute(colCellPlot, "pixbuf", 3)    # set params for icon
        w('treeview1').append_column(treeViewCol0)       # Append the columns to the TreeView

        treeViewCol = Gtk.TreeViewColumn("File")        # Create a TreeViewColumn
        colCellImg = Gtk.CellRendererPixbuf()       # Create a column cell to display an image
        colCellText = Gtk.CellRendererText()        # Create a column cell to display text
        treeViewCol.pack_start(colCellImg, expand=False)       # Add the cells to the column
        treeViewCol.pack_start(colCellText, expand=True)
        treeViewCol.add_attribute(colCellImg, "pixbuf", 1)      # Bind the image cell to column 1 of the tree's model
        treeViewCol.add_attribute(colCellText, "text", 2)       # Bind the text cell to column 0 of the tree's model
        w('treeview1').append_column(treeViewCol)       # Append the columns to the TreeView
        w('treeview1').set_expander_column(treeViewCol)

        w('treeview1').set_model(self.treestore1)       # Append the columns to the TreeView
        w('treeview1').set_enable_tree_lines(True) 
        w('treeview1').connect("row-expanded", self.onRowExpanded)       # add "on expand" callback
        w('treeview1').connect("row-collapsed", self.onRowCollapsed)         # add "on collapse" callback
        w('treeview1').get_selection().set_select_function(self.treeview1_selectmethod, data=None) # , full=True

        ## Select all input files at start, and plot them
        if len(sys.argv) > 1:    self.populateFileSystemTreeStore(self.treestore1, sys.argv[1], parent=None) ## TODO 
        else:                    self.populateFileSystemTreeStore(self.treestore1, os.path.dirname(os.getcwd()), parent=None) ## TODO 
        self.plot_reset()
        self.plot_all_sel_records()


        ## Add the data cursor by default  # TODO - make this work
        from matplotlib.widgets import Cursor
        cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        #}}}

    def treeview1_selectmethod(self, selection, model, treepath, is_selected, user_data):
        ## Expand a directory by clicking; do not allow selecting it
        treeiter        = self.treestore1.get_iter(treepath)
        filenamepath    = self.treestore1.get_value(treeiter, 0)
        itemMetaData    = os.stat(filenamepath) 
        itemIsFolder    = stat.S_ISDIR(itemMetaData.st_mode) # Extract metadata from the item
        if itemIsFolder:
            if w('treeview1').row_expanded(treepath):
                w('treeview1').collapse_row(treepath)
            else:
                w('treeview1').expand_row(treepath, open_all=False)
            return False
        else:
            return True
    ## === DATA HANDLING ===
    def add_record(self, file_path, tree_parent=None):
        ## Add the treeview item in the left panel

        #itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "empty", 8, 0) # Generate a default icon

        ## Register a new record in the record table
        self.record_labels[file_path] = os.path.basename(file_path) 
        self.record__types[file_path] = 'file'

    ## === FILE HANDLING ===
    def populateFileSystemTreeStore(self, treeStore, filepath, parent=None):
        itemCounter = 0
        listdir = os.listdir(filepath)
        listdir.sort()
        for item in listdir:                           # iterate over the items in the filepath
            itemFullname = os.path.join(filepath, item)             # Get the absolute filepath of the item
            itemMetaData = os.stat(itemFullname) 
            itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode) # Extract metadata from the item
            if itemIsFolder:
                icon = 'folder' # Determine if the item is a folder
            elif item[-4:] == '.dat':
                icon = 'empty'   ## if can not load, change icon to stock_dialog-warning
            else:
                icon = 'gtk-stop' 
            itemIcon = Gtk.IconTheme.get_default().load_icon(icon, 8, 0) # Generate a default icon




            #import cairo
#
            #WIDTH, HEIGHT = 256, 256
#
            #surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
            #ctx = cairo.Context (surface)
#
            #ctx.scale (WIDTH, HEIGHT) # Normalizing the canvas
#
            #pat = cairo.LinearGradient (0.0, 0.0, 0.0, 1.0)
            #pat.add_color_stop_rgba (1, 0.7, 0, 0, 0.5) # First stop, 50% opacity
            #pat.add_color_stop_rgba (0, 0.9, 0.7, 0.2, 1) # Last stop, 100% opacity
#
            #ctx.rectangle (0, 0, 1, 1) # Rectangle(x0, y0, x1, y1)
            #ctx.set_source (pat)
            #ctx.fill ()
#
            #ctx.translate (0.1, 0.1) # Changing the current transformation matrix
#
            #ctx.move_to (0, 0)
            #ctx.arc (0.2, 0.1, 0.1, -3./2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
            #ctx.line_to (0.5, 0.1) # Line to (x,y)
            #ctx.curve_to (0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
            #ctx.close_path ()
#
            #ctx.set_source_rgb (0.3, 0.2, 0.5) # Solid color
            #ctx.set_line_width (0.02)
            #ctx.stroke ()


            ##TODO
            #plotstyleIcon = Gtk.IconTheme.get_default().load_icon('empty', 8, 0) # Generate a default icon ## WORKS
            #plotstyleIcon = Pixbuf.new_from_file_at_size("img/logo.png", 125, 125) ## WORKS

            drawnpixbuf = Pixbuf.new(Colorspace.RGB, True, 8, 10, 10)
            color = 0xeeff2d
            print("%x" % color)
            drawnpixbuf.fill(color)
            #treestore.append(None, [drawnpixbuf, "data with a custom drawn image, which does not work"])

            #pixbuf = Pixbuf.new_from_file_at_size("img/logo.png", 125, 125) # Generate a default icon

#           drawable = Gdk.cairo_create(pixbuf)
#           #drawable = Gtk.GdkPixmap(None, 30, 30, 24)
#           gc = drawable.new_gc()
#           #drawable.draw_pixbuf(gc, pixbuf, 0, 0, 0, 0, -1, -1)
#           gc.set_foreground(Gtk.Gdk.Color(65535, 0, 0))
#           drawable.draw_line(gc, 0, 0, w, h)
#
#           cmap = Gtk.Gdk.Colormap(Gtk.Gdk.visual_get_best(), False)
#           pixbuf.get_from_drawable(drawable, cmap, 0, 0, 0, 0, w, h)


            plotstyleIcon = drawnpixbuf

#s = cairo_image_surface_create (CAIRO_FORMAT_A1, 3, 3);
#cr = cairo_create (s);
#cairo_arc (cr, 1.5, 1.5, 1.5, 0, 2 * M_PI);
#cairo_fill (cr);
#cairo_destroy (cr);
#
#pixbuf = gdk_pixbuf_get_from_surface (s,
                                      #0, 0,
                                      #3, 3);
#
#cairo_surface_destroy (s);

            ## OPTION 4
            #cairo_context = self.canvas.get_window().cairo_create()
#
            #window = w('treeview1').get_window()
#
            #ctx = Gdk.cairo_create(window)
            #ctx.set_source_pixbuf(pixbuf, 0, 0)
            #self.image = cairo.ImageSurface.create_from_png('img/logo.png')

            ## OPTION 5
            # ?? Gdk.cairo_set_source_pixbuf() 







            currentIter = treeStore.append(parent, [itemFullname, itemIcon, item, plotstyleIcon])  # Append the item to the TreeStore
            if itemIsFolder: treeStore.append(currentIter, self.dummy_treestore_row)      # add dummy if current item was a folder
            itemCounter += 1                                    #increment the item counter
        if itemCounter < 1: treeStore.append(parent, self.dummy_treestore_row)        # add the dummy node back if nothing was inserted before

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
        treeStore.append(treeIter, self.dummy_treestore_row)      # append dummy node
    

    ## === GRAPHICAL PRESENTATION ===
    def plot_reset(self):
        self.ax.cla() ## TODO clearing matplotlib plot - this is inefficient, rewrite

        ## TODO for all liststore rows, reset the plotting color to white


    def plot_all_sel_records(self):
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if len(pathlist) == 0: return

        ## Generate the color palette
        #color_palette = ["g"]*len(pathlist) ## TODO use some real palette
        color_palette = matplotlib.cm.gist_rainbow(np.linspace(0.00, 0.95, len(pathlist)+1)[:-1])

        ## Erase all color fields in the list
        treeiter = self.treestore1.get_iter_first()

        ## TODO: set some empty icon for not plotted lines
        #while treeiter != None: 
                #self.treestore1.set_value(treeiter, 4, 'no') ## empty field means not plotted
                #treeiter=self.treestore1.iter_next(treeiter)

        ## Plot all curves sequentially
        error_counter = 0
        for (path, color_from_palette) in zip(pathlist, color_palette):
            try:
                ## Plot the line first
                file_name = self.treestore1.get_value(self.treestore1.get_iter(path), 0)
                self.plot_record(file_name, plot_style={'color':color_from_palette})

                ## If no exception occurs, color the background of the "plot" column according to the line 
                c1,c2,c3 = 256*color_from_palette[0:3] - .5
                hexcode_from_palette = '#%02x%02x%02x' % (int(c1), int(c2), int(c3)) # list(np.int(256*color_from_palette[0:3]))

                ## TODO generate a new coloured icon
                #self.treestore1.set_value(self.treestore1.get_iter(path), 3, hexcode_from_palette)
                 #self.treestre1.set_value(self.

            except ValueError:
                traceback.print_exc()
                error_counter += 1
        self.ax.legend(loc="upper right")
        self.ax.grid(True)
        w('statusbar1').push(0,"During last file-selection operation, %d errors were encountered" % error_counter)

    def plot_record(self, infile, plot_style={}):
        ## Plotting "on-the-fly", i.e., program does not store any data and loads them from disk upon every (re)plot
        x, y = np.genfromtxt(infile, usecols=[0,1], unpack=True,  dtype=type(0.0), 
                comments='#', delimiter=None, skip_header=0, skip_footer=0,           ## default options follow...
                converters=None, missing_values=None, filling_values=None, names=None, excludelist=None, 
                deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', 
                usemask=False, loose=True, invalid_raise=True) # , max_rows=None ## does not work with older numpy?
                # TODO apply file loading options

        ## Plot the curve in the right panel
        self.ax.plot(x, y, label=os.path.basename(infile), **plot_style) # TODO apply plotting options

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


    # future todos:
    #  * select record by clicking in the graph, right-click menu in the list)
    #        http://scienceoss.com/interactively-select-points-from-a-plot-in-matplotlib/#more-14
    #        http://scienceoss.com/interacting-with-figures-in-python/
    #  * line as actor?   ... self.line, = self.Axes.plot([], [], animated=True)
    #                         self.background=self.canvas1.copy_from_bbox(self.Axes.bbox)
    #  * allow PDF graph export   
            # TODO - use icons?
            #w('treestore1').append(None, ['no', Gtk.IconTheme.get_default().load_icon('edit-cut', 16, 0), infile])
            # TODO - moving rows http://www.pygtk.org/pygtk2tutorial/sec-TreeModelInterface.html

            # TODO - on window resize, adjust borders? 
            # http://stackoverflow.com/questions/6066091/python-matplotlib-figure-borders-in-wxpython
