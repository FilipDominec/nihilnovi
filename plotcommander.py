#!/usr/bin/python3
#-*- coding: utf-8 -*-

import gi, sys, os, signal, stat, warnings, re
import numpy as np
from scipy.constants import c,h,e
import traceback, faulthandler ## Debugging library crashes
faulthandler.enable()
# https://docs.python.org/3/library/sys.html#sys.settrace

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

import liborigin
import robust_csv_parser
import sort_alpha_numeric

default_plot_command = \
"""for x, y, parameters, ylabel, xlabel, ylabel, color_from_palette in \
        zip(xs, ys, params, labels, xlabels, ylabels, color_palette):
    self.ax.plot(x, y, label=ylabel, color=color_from_palette) """

class Handler:
    ## == initialization == 
    def __init__(self): #{{{
        self.lockTreeViewEvents = False
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

        self.opj_file_cache = {}

        ## TreeStore and ListStore initialization
        self.tsFiles = Gtk.TreeStore(str,          Pixbuf,   str,      Pixbuf,            int,        int,             str)
        self.treeStoreColumns =     {'filepath':0, 'icon':1, 'name':2, 'plotstyleicon':3, 'column':4, 'spreadsheet':5, 'rowtype':6}
        self.dummy_treestore_row = [None for x in self.treeStoreColumns.keys()]

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
        w('treeview1').set_model(self.tsFiles)       # Append the columns to the TreeView
        w('treeview1').get_selection().set_select_function(self.treeview1_selectmethod, data=None) # , full=True

        ## TODO: If files are specified as arguments, select these at start, and plot them at once

        ## If a directory is specified, just set it as the root of the file list. If none, use current working dir.
        self.populateTreeStore(self.tsFiles, reset_path=os.getcwd() if len(sys.argv)<=1  else  sys.argv[1])
        self.plot_reset()
        self.plot_all_sel_records()

        ## Initialize the default plotting commands 
        w('txt_rc').get_buffer().set_text(default_plot_command)

        ## Add the data cursor by default  # TODO - make this work
        from matplotlib.widgets import Cursor
        cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        #}}}
    ## === FILE HANDLING ===
    def is_dir(self,filename): # {{{
        return stat.S_ISDIR(os.stat(filename).st_mode)
        # }}}
    def row_type_from_fullpath(self, fullpath):# {{{
        """
        Known row types:

            #Type                   row_is_leaf row_can_plot    row_icon
            dir                     0           0               ''
            updir                   1           0               'go-up'
            csvtwocolumn            1           1               ''
            csvmulticolumn          0           0               ''
            xlsfile                 0           0               ''
            xlsspread               0           0               ''
            xlscolumn               1           1               ''
            opjfile                 0           0               ''
            opjgraph                0           0               ''
            opjspread               0           0               ''
            opjcolumn               1           1               ''
            unknown                 1           0               ''
        """
        ## Note: Remaining row types not returned by this function (i.e. xlsspread, xlscolumn, opjgraph etc.) are 
        ## never assigned to files; they are added only when a file or spreadsheet is unpacked and populated.
        ## The determination of file type from its name is a bit sloppy, but it works and it is fast. 
        assert isinstance(fullpath, str)

        if self.is_dir(fullpath):
            return 'dir'
        elif fullpath.lower().endswith('.csv') or fullpath.lower().endswith('.dat') or fullpath.lower().endswith('.txt'):
            try:
                ## Note: column number is incorrectly determined if header is longer than sizehint, but 10kB should be enough
                data_array, header, parameters = robust_csv_parser.loadtxt(fullpath, sizehint=10000)
                return 'csvtwocolumn' if len(header)==2 else 'csvmulticolumn'
            except (IOError, RuntimeError):    # This error is usually returned for directories and non-data files
                return 'unknown'
        elif fullpath.lower().endswith('.xls'):
            ## TODO XLS support : determine if single spreadsheet, and/or if spreadsheet(s) contain single column
            return 'xlsfile'
        elif fullpath.lower().endswith('.opj'):
            return 'opjfile'
        else:
            return 'unknown'

        # }}}
    def rowtype_is_leaf(self, rowtype):# {{{
        """ Determines if row shall be selected (or unpacked, otherwise)
        
        Rows representing containers (e.g. directories, multicolumn CSV files or Origin files)  
        are not "leaves", since they contain some structure that can be further unpacked. In contrast, 
        ordinary two-column CSV files or columns of CSV files are "leaves" and can be directly plotted.
        """
        return (rowtype in ('csvtwocolumn', 'csvcolumn', 'xlscolumn', 'opjcolumn', 'unknown'))
    # }}}
    def rowtype_can_plot(self, rowtype):# {{{
        """ Determines if row shall be plotted """
        return (rowtype in ('csvtwocolumn', 'xlscolumn', 'opjcolumn'))
    # }}}
    def rowtype_icon(self, rowtype, iconsize=8):# {{{
        iconname = {
                'updir':            'go-up',
                'dir':              'folder',
                'csvtwocolumn':     'empty',
                'csvmulticolumn':   'zip', 
                'csvcolumn':        'empty', 
                'opjfile':          'zip', 
                'opjspread':        'go-next', 
                'opjgraph':         'go-previous', 
                'opjcolumn':        'empty', 
                'xlsfile':          'zip', 
                'xlsspread':        'go-next', 
                'xlscolumn':        'empty', 
                'unknown':          'stop'
                }
        return Gtk.IconTheme.get_default().load_icon(iconname[rowtype], iconsize, 0)
    # }}}
    def origin_parse_or_cache(self, basepath):# {{{
        if basepath in self.opj_file_cache.keys():      
            return self.opj_file_cache[basepath]
        else: 
            opj = liborigin.parseOriginFile(basepath)
            self.opj_file_cache[basepath] = opj
            return opj
        # }}}
    def populateTreeStore(self, treeStore, parent_row=None, reset_path=None):
        ## without any parent specified, rows will be added to the very left of the TreeView, 
        ## otherwise they will become childs thereof
        if parent_row is None:
            if reset_path is not None:
                basepath = reset_path
            else:
                if self.row_prop(self.tsFiles.get_iter_first(), 'rowtype') == 'updir':
                    basepath = self.row_prop(self.tsFiles.get_iter_first(), 'filepath')
                else:
                    raise AttributeError('Specify either parent_row, reset_path, or ensure the first row is of "updir" type')

            ## On startup, or when the 'updir' node is selected, we update the whole tree. 
            ## Initially, it has to be cleared of all rows. 
            ## During this operation, its selection will change, but the plots should not be updated so that it is fast.
            self.lockTreeViewEvents = True
            self.tsFiles.clear()            ## TODO: remember the unpacked rows, and also the selected ones
            self.clearAllPlotIcons(self.tsFiles.get_iter_first())  ## TODO: obsolete, rm!
            self.lockTreeViewEvents = False

            ## The first node of cleared treeStore will point to the above directory, enabling one to browse whole filesystem 
            plotstyleIcon = Pixbuf.new(Colorspace.RGB, True, 8, 10, 10)
            plotstyleIcon.fill(0xffffffff)
            currentIter = treeStore.append(None, 
                    [basepath, self.rowtype_icon('updir'), '..', plotstyleIcon, None, None, 'updir'])
                        ## ^^ FIXME basepath? or os.path.dirname(basepath) ?
            treeStore.append(currentIter, self.dummy_treestore_row)
        elif parent_row is not None  and  reset_path is None:
            ## If not resetting the whole tree, get the basepath from the parent row
            basepath = treeStore.get_value(parent_row, self.treeStoreColumns['filepath'])
        else:
            raise()

        ## Prepare the lists of paths, column numbers and spreadsheet numbers to be added
        parentrowtype = self.row_prop(parent_row, 'rowtype') if parent_row else 'dir'
        assert not self.rowtype_is_leaf(parentrowtype)
        if parentrowtype == 'dir':             ## Populate a directory with files/subdirs
            ## Get the directory contents, filtering the files
            fileFilterString = w('enFileFilter').get_text().strip()
            filenames = [n for n in os.listdir(basepath) if (fileFilterString in os.path.basename(basepath))]
            print(filenames)

            ## Sort alphabetically, all folders above files
            filenames = sorted(filenames, key=sort_alpha_numeric.split_alpha_numeric)   # intelligent alpha/numerical sorting
            itemFullNames = [os.path.join(basepath, filename) for filename in filenames]
            itemFullNames = ([ f for f in itemFullNames if     self.is_dir(f)] 
                            + [f for f in itemFullNames if not self.is_dir(f)])         # dirs will be listed first, files below
            itemShowNames = [os.path.split(f)[1] for f in itemFullNames]                # only file name without path will be shown
            columnNumbers = [None] * len(itemFullNames)    # obviously files/subdirs are assigned no column number
            spreadNumbers = [None] * len(itemFullNames)    # nor they are assigned any spreadsheet number
            rowTypes      = [self.row_type_from_fullpath(f) for f in itemFullNames]
        elif parentrowtype == 'csvmulticolumn':
            ## Note: Multicolumn means at least 3 columns (i.e. x-column and two or more y-columns)
            data_array, header, parameters = robust_csv_parser.loadtxt(basepath, sizehint=10000)
            columnFilterString = w('enColFilter').get_text().strip()
            if columnFilterString != "": header = [n for n in header if (fileFilterString in n)]
            itemFullNames = [basepath] * len(header)    # all columns are from one file
            itemShowNames = header                      # column numbers are either in file header, or auto-generated
            columnNumbers = list(range(len(header)))    # enumerate the columns
            spreadNumbers = [None] * len(header)        # there are no spreadsheets in CSV files
            rowTypes      = ['csvcolumn'] * len(header)
        elif parentrowtype == 'opjfile':
            opj = self.origin_parse_or_cache(basepath)
            ## Add "graphs" - which show the selected columns in presentation-ready format
            ## Fixme support for multiple opjlayers also here
            itemShowNames = ['%s "%s"' % (graph.name.decode('utf-8'), graph.label.decode('utf-8')) for graph in opj['graphs']]
            itemFullNames = [basepath] * len(itemShowNames)    # all columns are from one file
            columnNumbers = [None] * len(itemShowNames)
            spreadNumbers = list(range(len(itemShowNames)))  
            rowTypes      = ['opjgraph'] * len(itemShowNames)

            ## Add "columns" - which enable to access all data in the file, including those not used in "graphs"
            itemShowNames = itemShowNames + ['%s "%s"' % (spread.name.decode('utf-8'), spread.label.decode('utf-8')) 
                    for spread in opj['spreads']]
            itemFullNames = itemFullNames + [basepath] * len(itemShowNames)    # all columns are from one file
            columnNumbers = columnNumbers + [None] * len(itemShowNames)
            spreadNumbers = spreadNumbers + list(range(len(itemShowNames)))  
            rowTypes      = rowTypes      + ['opjspread'] * len(itemShowNames)
        elif parentrowtype == 'opjspread':
            opj = self.origin_parse_or_cache(basepath)
            parent_spreadsheet = self.row_prop(parent_row, 'spreadsheet')
            itemShowNames = [column.name.decode('utf-8') for column in opj['spreads'][parent_spreadsheet].columns]
            itemFullNames = [basepath] * len(itemShowNames)    # all columns are from one file
            columnNumbers = list(range(len(itemShowNames)))  
            spreadNumbers = [parent_spreadsheet] * len(itemShowNames)
            rowTypes      = ['opjcolumn'] * len(itemShowNames)
        elif parentrowtype == 'opjgraph':
            opj = self.origin_parse_or_cache(basepath)
            parent_graph = self.row_prop(parent_row, 'spreadsheet') ## The key 'spreadsheet' is misused here to mean 'graph'
            layerNumber = 0 ## Fixme support for multiple opjlayers:    ["graphs"][1].layers[0].curves[3].xColumnName

            ## Try to extract meaningful legend for each curve, assuming the legend box has the same number of lines
            curves = opj['graphs'][parent_graph].layers[layerNumber].curves
            legend_box = opj['graphs'][parent_graph].layers[layerNumber].legend.text.decode('utf-8').split('\n')
            if len(legend_box) >= len(curves):
                ## the legend may have format as such: ['\l(1) 50B', '\l(2) 48B', ...], needs to be pre-formatted:
                legends = [re.sub(r'\\l\(\d\)\s', '', legend_row.strip()) for legend_row in legend_box[:len(curves)]]
                comment = "".join([legendrow.strip() for legendrow in legend_box[:len(curves)]])
                ## todo: \g(l)\-(ex) should translate into (greek lambda)_ex
                ## def togreek(l): return chr(ord(l) + ord('α') - ord('a'))
                ## string.ascii_letters, "".join([togreek(g) for g in string.ascii_letters])
                ## 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
                ## 'αβγδεζηθι κλμνοπρςστυφχξψωΑΒΓΔΕΖΗΘΙ ΚΛΜΝΟΠ ΡΣΤΥΦΧΞΨΩ'
                print(legends, comment)
            else:
                legends = [""] * len(curves)
                comment = ""

            itemShowNames, itemFullNames, columnNumbers, spreadNumbers = [], [], [], []
            for curve, legend in zip(curves, legends):
                ## FIXME add support for xColumn different than the first one in Spreadsheet, also here
                #print("curve t xCol yCol:", curve.dataName.decode('utf-8'), 
                        #curve.xColumnName.decode('utf-8'), curve.yColumnName.decode('utf-8'))
                #print([spread.name for spread in opj['spreads']], (curve.dataName[2:]))

                ## Seek the corresponding spreadsheet and column by their name
                spreadsheet_index = [spread.name for spread in opj['spreads']].index(curve.dataName[2:])
                spread = opj['spreads'][spreadsheet_index]
                y_column_index = [column.name for column in spread.columns].index(curve.yColumnName)
                x_column_index = [column.name for column in spread.columns].index(curve.xColumnName)
                #print(curve.dataName[2:].decode('utf-8'), spreadsheet_index, curve.yColumnName.decode('utf-8'), y_column_index)

                itemShowNames.append('%s -> spread %s "%s": column %s (against  %s)' % 
                        (legend, spread.name.decode('utf-8'), spread.label.decode('utf-8'), 
                                spread.columns[y_column_index].name.decode('utf-8'), 
                                spread.columns[x_column_index].name.decode('utf-8')))
                itemFullNames.append(basepath)          # all columns are from one file
                columnNumbers.append(y_column_index)  
                spreadNumbers.append(spreadsheet_index)
            rowTypes      = ['opjcolumn'] * len(itemShowNames) ## TODO or introduce opjgraphcurve ?
        else:
            warnings.warn('Not prepared yet to show listings of this file: %s' % parentrowtype)
            return


        ## Go through all items and populate the node
        itemCounter = 0
        for itemFullName, itemShowName, columnNumber, spreadNumber, rowtype in \
                zip(itemFullNames, itemShowNames, columnNumbers, spreadNumbers, rowTypes):
            plotstyleIcon = Pixbuf.new(Colorspace.RGB, True, 8, 10, 10)
            plotstyleIcon.fill(0xffffffff)
            currentIter = treeStore.append(parent_row, 
                    [itemFullName, self.rowtype_icon(rowtype), itemShowName, plotstyleIcon, columnNumber, spreadNumber, rowtype])
            if not self.rowtype_is_leaf(rowtype): ## TODO row---> parentrowtype
                treeStore.append(currentIter, self.dummy_treestore_row)     # shows the "unpacking arrow" left of the item
            itemCounter += 1                                    #increment the item counter
        if itemCounter < 1: treeStore.append(parent_row, self.dummy_treestore_row)        # add the dummy node back if nothing was inserted before
        ## TODO ^^ shall be removed?



    ## === GRAPHICAL PRESENTATION ===
    def clearAllPlotIcons(self, treeIter):# {{{
        while treeIter != None: 
            iterpixbuf = self.row_prop(treeIter, 'plotstyleicon')
            if iterpixbuf: iterpixbuf.fill(self.array2rgbhex([.5,.5,1], alpha=0)) ## some nodes may have pixbuf set to None
            self.clearAllPlotIcons(self.tsFiles.iter_children(treeIter))
            treeIter=self.tsFiles.iter_next(treeIter)
        # }}}
    def array2rgbhex(self,arr3,alpha=1): # {{{
        return  int(arr3[0]*256-.5)*(256**3) +\
                int(arr3[1]*256-.5)*(256**2) +\
                int(arr3[2]*256-.5)*(256**1) +\
                int(alpha*255  -.5)
        # }}}
    def plot_reset(self):# {{{
        self.ax.cla() ## TODO clearing matplotlib plot - this is inefficient, rewrite

        def recursive_clear_icon(treeIter):
            while treeIter != None: 
                iterpixbuf = self.tsFiles.get_value(treeIter, 3)
                if iterpixbuf: iterpixbuf.fill(self.array2rgbhex([.5,.5,1], alpha=0)) ## some nodes may have pixbuf set to None
                recursive_clear_icon(self.tsFiles.iter_children(treeIter))
                treeIter=self.tsFiles.iter_next(treeIter)
        recursive_clear_icon(self.tsFiles.get_iter_first())
        w('treeview1').queue_draw()
        # }}}
    def load_row_data(self, row):# {{{
        """ loads all relevant data for a given treestore row, and returns: x, y, label, parameters, xlabel, ylabel

        Plotting is "on-the-fly", i.e., program does not store any data (except OPJ file cache) and loads them 
        from disk upon every (re)plot.
        """
       

        ## Load the data
        rowfilepath = self.row_prop(row, 'filepath')
        rowtype     = self.row_prop(row, 'rowtype')
        rowxcolumn  = 0 ## TODO allow ordinate also on >0th column 
        rowycolumn  = self.row_prop(row, 'column')
        rowsheet    = self.row_prop(row, 'spreadsheet')
        if  rowtype == 'opjcolumn':
            opj = liborigin.parseOriginFile(rowfilepath)
            # TODO: what does opj['spreads'][3].multisheet mean?
            x, y = [opj['spreads'][rowsheet].columns[c].data for c in [rowxcolumn, rowycolumn]]
            if len(x)>2 and x[-2]>x[-1]*1e6: x=x[:-1]       ## the last row from liborigin is sometimes erroneous zero
            y = y[0:len(x)]                                 ## truncate y if longer than x
            try:                                    ## fast string-to-float conversion
                x, y = [np.array(arr) for arr in (x,y)] ## TODO dtype=float
            except ValueError:                      ## failsafe string-to-float conversion
                x0, y0 = [], []
                for x1,y1 in zip(x,y):
                    try:
                        xf, yf = float(x1), float(y1)
                        x0.append(xf); y0.append(yf)
                    except ValueError:
                        pass
                x,y = x0, y0
            xlabel, ylabel = [opj['spreads'][rowsheet].columns[c].name.decode('utf-8') for c in [rowxcolumn, rowycolumn]] 
            parameters = {} ## todo: is it possible to load parameters from origin column?
            return x, y, ylabel, parameters, xlabel, ylabel
        elif rowtype == 'csvtwocolumn':
            ycolumn = 1
            data_array, header, parameters = robust_csv_parser.loadtxt(rowfilepath, sizehint=1000000)
            return  data_array.T[0], data_array.T[1], header[1], parameters, header[0], header[1]
        elif rowtype == 'csvcolumn':
            data_array, header, parameters = robust_csv_parser.loadtxt(rowfilepath, sizehint=1000000)
            return data_array.T[rowxcolumn], data_array.T[rowycolumn], header[rowycolumn], parameters, \
                    header[rowxcolumn], header[rowycolumn]
        #elif rowtype == 'xls':
            # TODO a XLS file is a *container* with multiple sheets, a sheet may contain multiple columns
            #return 
            #xl = pd.ExcelFile(infile, header=1) ##  
            #print(xl.sheet_names)  
            #print(xl.sheets[rowsheet])
            #df = xl.parse() 
            #x, y, xlabel, ylabel = df.values.T[rowxcolumn], df.values.T[rowycolumn], header[rowxcolumn], header[rowycolumn]
            ## TODO Should offer choice of columns ## FIXME clash with 'header'!!
        else:
            raise RuntimeError         ## for all remaining filetypes, abort plotting quietly

# }}}
    def plot_all_sel_records(self):# {{{

        ## Load all row data
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if len(pathlist) == 0: return
        error_counter = 0
        row_data = []
        plotted_paths = []
        for path in pathlist:
            try:
                row_data.append(self.load_row_data(self.tsFiles.get_iter(path)))
                plotted_paths.append(path)
            except (RuntimeError, ValueError):
                traceback.print_exc()
                error_counter += 1
        xs, ys, params, labels, xlabels, ylabels = zip(*row_data)
        w('statusbar1').push(0, "During last file-selection operation, %d errors were encountered" % error_counter)

        ## Generate the color palette for curves
        color_pre_map = np.linspace(0.05, .95, len(plotted_paths)+1)[:-1]
        color_palette = matplotlib.cm.gist_rainbow(color_pre_map*.5 + np.sin(color_pre_map*np.pi/2)**2*.5)
        for path, color_from_palette in zip(plotted_paths, color_palette):
            ## If no exception occured during loading, colour the icon according to the line colour
            icon = self.row_prop(self.tsFiles.get_iter(path), 'plotstyleicon')
            if icon: icon.fill(self.array2rgbhex(color_from_palette))
            plotted_paths.append(path)

        ## Plot all curves sequentially
        plot_cmd_buffer = w('txt_rc').get_buffer() 
        plot_command = plot_cmd_buffer.get_text(plot_cmd_buffer.get_start_iter(), plot_cmd_buffer.get_end_iter(), 
                include_hidden_chars=True)
        if plot_command.strip() != "":
            exec(plot_command)
        else:
            plot_command = default_plot_command
            plot_cmd_buffer.set_text(default_plot_command)

        #self.ax.legend(loc="auto")
        self.ax.grid(True)
        self.ax.set_xscale('log' if w('chk_xlogarithmic').get_active() else 'linear')
        self.ax.set_yscale('log' if w('chk_ylogarithmic').get_active() else 'linear')
        #if w('chk_legend').get_active(): self.ax.legend(True)
        #if w('chk_autoscale').get_active():
            #self.ax.relim()
            #self.ax.autoscale_view()
        self.canvas.draw()


        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        # }}}
    ## == FILE AND DATA UTILITIES ==
    def row_prop(self, row, prop):# {{{
        return self.tsFiles.get_value(row, self.treeStoreColumns[prop])
        # }}}
    def remember_treeView_expanded_rows(self, treeStore, treeView):    # {{{
        ## returns a list of paths of expanded files/directories
        expanded_row_names = []
        def remember_treeview_states(treeIter):
            while treeIter != None: 
                if w('treeview1').row_expanded(treeStore.get_path(treeIter)):
                    expanded_row_names.append(treeStore.get_value(treeIter, 0))      # get the full path of the position
                remember_treeview_states(treeStore.iter_children(treeIter))
                treeIter=treeStore.iter_next(treeIter)
        remember_treeview_states(treeStore.get_iter_first())
        return expanded_row_names
        # }}}
    def remember_treeView_selected_rows(self, treeStore, treeView):# {{{
        ## returns a list of paths of selected files/directories
        (model, selectedPathList) = treeView.get_selection().get_selected_rows()
        selected_row_names = []
        for treePath in selectedPathList:
            selected_row_names.append(treeStore.get_value(treeStore.get_iter(treePath), 0))
        return selected_row_names
        # }}}
    def restore_treeView_expanded_rows(self, expanded_row_names):# {{{
        def recursive_expand_rows(treeIter, ):
            while treeIter != None: 
                if self.tsFiles.get_value(treeIter, 0) in expanded_row_names:
                    self.lockTreeViewEvents = True
                    w('treeview1').expand_row(self.tsFiles.get_path(treeIter), open_all=False)
                    self.lockTreeViewEvents = False
                recursive_expand_rows(self.tsFiles.iter_children(treeIter))
                treeIter=self.tsFiles.iter_next(treeIter)
        recursive_expand_rows(self.tsFiles.get_iter_first())
        # }}}
    def restore_treeView_selected_rows(self, selected_row_names):# {{{
        def recursive_select_rows(treeIter):
            while treeIter != None: 
                if self.tsFiles.get_value(treeIter, 0) in selected_row_names:
                    w('treeview1').get_selection().select_path(self.tsFiles.get_path(treeIter))
                recursive_select_rows(self.tsFiles.iter_children(treeIter))
                treeIter=self.tsFiles.iter_next(treeIter)
        recursive_select_rows(self.tsFiles.get_iter_first())
        self.plot_all_sel_records()
        # }}}

    ## == USER INTERFACE HANDLERS ==
    def on_treeview1_row_expanded(self, treeView, treeIter, treePath):# {{{
        ## if present, remove the dummy node (which is only used to draw the expander arrow)
        treeStore = treeView.get_model()
        newFilePath = treeStore.get_value(treeIter, 0)      # get the full path of the position

        ## Add the children 
        self.populateTreeStore(treeStore, parent_row=treeIter)

        ## The dummy row has to be removed AFTER this, otherwise the empty treeView row will NOT expand)
        if treeStore.iter_children(treeIter):  
            treeStore.remove(treeStore.iter_children(treeIter))         
    #}}}
    def on_treeview1_row_collapsed(self, treeView, treeIter, treePath):# {{{ 
        ## Remove all child nodes of the given row (useful mostly to prevent de-syncing from some changes in the filesystem)
        #if self.lockTreeViewEvents: return      ## prevent event handlers triggering other events
        currentChildIter = self.tsFiles.iter_children(treeIter)
        while currentChildIter:         
            self.tsFiles.remove(currentChildIter)
            currentChildIter = self.tsFiles.iter_children(treeIter)
        self.tsFiles.append(treeIter, self.dummy_treestore_row)
    # }}}
    def on_treeview1_selection_changed(self, *args):# {{{       ## triggers replot
        if self.lockTreeViewEvents: return      ## prevent event handlers triggering other events
        ## Update the graphical presentation
        self.plot_reset()               ## first delete the curves, to hide (also) unselected plots
        self.plot_all_sel_records()     ## then show the selected ones
    # }}}
    def treeview1_selectmethod(self, selection, model, treePath, is_selected, user_data):# {{{
        ## TODO reasonable behaviour for block-selection over different unpacked directories/files
        ## Expand a directory by clicking, but do not allow user to select it
        treeIter        = self.tsFiles.get_iter(treePath)
        self.treeStoreColumns=      {'filepath':0, 'icon':1, 'name':2, 'plotstyleicon':3, 'column':4, 'spreadsheet':5, 'rowtype':6}

        #if self.lockTreeViewEvents: return      ## prevent event handlers triggering other events OBSOLETED?
        #lockTreeViewEvents_tmp = self.lockTreeViewEvents       ## TODO understand and clear out when select events can occur
        #self.lockTreeViewEvents = True
        # ...
        #self.lockTreeViewEvents = lockTreeViewEvents_tmp

        ## Clicking action of non-leaf un-selectable rows:
        rowtype = self.tsFiles.get_value(treeIter, self.treeStoreColumns['rowtype'])
        if self.rowtype_is_leaf(rowtype):       
            return True                                     ## allow selecting or unselecting
        else:
            if rowtype == "updir":  
                ## If the expanded row was "..", do not expand it, instead change to up-dir and refresh whole tree
                expanded_row_names = self.remember_treeView_expanded_rows(self.tsFiles, w('treeview1'))    
                selected_row_names = self.remember_treeView_selected_rows(self.tsFiles, w('treeview1'))
                self.populateTreeStore(self.tsFiles, reset_path=os.path.dirname(self.row_prop(treeIter, 'filepath')))       
            elif w('treeview1').row_expanded(treePath):
                w('treeview1').collapse_row(treePath)
            elif not w('treeview1').row_expanded(treePath) :
                w('treeview1').expand_row(treePath, open_all=False)
            return False

# }}}
    def on_enFileFilter_activate(self, *args):# {{{
        expanded_row_names = self.remember_treeView_expanded_rows(self.tsFiles, w('treeview1'))    
        selected_row_names = self.remember_treeView_selected_rows(self.tsFiles, w('treeview1'))
        # Passing parent=None will populate the whole tree again
        #self.lockTreeViewEvents = True
        self.populateTreeStore(self.tsFiles, reset_path=None)       
        #self.lockTreeViewEvents = False
        self.restore_treeView_expanded_rows(expanded_row_names)
        self.restore_treeView_selected_rows(selected_row_names)
        # }}}
    def on_enFileFilter_focus_out_event(self, *args):# {{{
        self.on_enFileFilter_activate(self)
    # }}}
    def on_enColFilter_activate(self, *args):# {{{ TODO
        pass
    def on_enColFilter_focus_out_event(self, *args):
        pass
# }}}
    def on_window1_delete_event(self, *args):# {{{
        Gtk.main_quit(*args)# }}}

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
    #  * https://www.python.org/dev/peps/pep-0257/ - Docstring Conventions
    #  * PEP8: . In Python 3, "raise X from Y" should be used to indicate explicit replacement without losing the original traceback. 
    #  * 'keramika 06062016.opj' and 'srovnani27a28.opj'  makes liborigin eat up all memory
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
