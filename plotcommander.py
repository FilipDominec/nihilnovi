#!/usr/bin/python3
#-*- coding: utf-8 -*-



import gi, sys, os, signal, stat, warnings, re, time
import numpy as np
import scipy.constants as sc
import traceback, faulthandler ## Debugging library crashes
faulthandler.enable()
# https://docs.python.org/3/library/sys.html#sys.settrace

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango
from gi.repository.GdkPixbuf import Pixbuf, Colorspace

import matplotlib
import matplotlib.cm as cm
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo  as FigureCanvas # "..Agg" backend is broken currently
from matplotlib.backends.backend_gtk3      import NavigationToolbar2GTK3 as NavigationToolbar # if not specified, Python3 freezes
#from mpl_toolkits.axes_grid1 import host_subplot ## allows better axes handling than fig.subplot
from matplotlib.widgets import Cursor

import robust_csv_parser
import sort_alpha_numeric

## User settings       TODO -> external config file
## TODO These settings should be loaded dynamically from ./plotcommanderrc.py, ../plotcommanderrc.py, ../../plotcommanderrc.py, ...
#matplotlib.rcParams['font.family'] = 'serif'        
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.linewidth'] = .5
matplotlib.rcParams['savefig.facecolor'] = "white"

SIZELIMIT_FOR_HEADER = 10000
SIZELIMIT_FOR_DATA   = 10000000

external_editor_command = ('/usr/bin/vim.gtk', '-gp')

line_plot_command = \
"""matplotlib.rc('font', size=12, family='serif')
for          x,  y,  n,              param,  label,  xlabel,  ylabel,  color in \\\n         zip(xs, ys, range(len(xs)), params, labels, xlabels, ylabels, colors):
    # x, y = x[~np.isnan(y)], y[~np.isnan(y)]        ## filter-out NaN points
    # convol = 2**-np.linspace(-2,2,25)**2; y = np.convolve(y,convol/np.sum(convol), mode='same') ## simple smoothing

    ax.plot(x, y, label="%s" % (label), color=color)
    #ax.plot(x, y, label="%s" % (label.split('.dat')[0]), color=colors[c%10], ls=['-','--'][int(c/10)]) 
ax.set_xlabel(xlabelsdedup)
ax.set_ylabel(ylabelsdedup)

plot_title = sharedlabels[-4:] ## last few labels that are shared among all curves make a perfect title
#plot_title = sharedlabels[sharedlabels.index('LastCroppedLabel')+1:] ## optionally, use all labels after the chosen one 

#ax.set_xlim(xmin=0, xmax=1)
#ax.set_ylim(ymin=2.6, ymax=2.7)
#ax.set_xscale('log')
#ax.set_yscale('log')
ax.set_title(' '.join(plot_title)) 
ax.legend(loc='best', prop={'size':10})

#np.savetxt('output.dat', np.vstack([x,ys[0],ys[1]]).T, fmt="%.8g")
#tosave.append('_'.join(plot_title)+'.png') ## whole graph will be saved as PNG
#tosave.append('_'.join(plot_title)+'.pdf') ## whole graph will be saved as PDF
"""

contour_plot_command = \
"""matplotlib.rc('font', size=12)
ys = np.array(ys)
cmaprange1, cmaprange2 = np.min(ys), np.max(ys) 
param = np.linspace(1, 2, len(ys))
levels = np.linspace(cmaprange1, cmaprange2, 50) 

#   # Grid the data, produce interpolated quantities:
#   from matplotlib.mlab import griddata
#   min_xs,       max_xs,    min_params,   max_params = min(xs),       max(xs),    min(params),   max(params)
#   xi      = np.linspace(min_xs,       max_xs,       args.contourresx)
#   paramsi = np.linspace(min_params,   max_params,   args.contourresp)
#   interp_anisotropy = (max_xs-min_xs)/(max_params-min_params) * args.interp_aspect 
#   yi      = griddata(xs, params*interp_anisotropy, ys, xi, paramsi*interp_anisotropy, interp='linear')

ax.contourf(xs[0], param, ys, levels=levels, extend='both')
ax.contour(xs[0], param, ys, levels=levels)
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('')
"""



"""
ys = np.array(ys)
cmaprange1, cmaprange2 = np.min(ys), np.max(ys) 
levels = 10**(np.linspace(np.log10(cmaprange1), np.log10(cmaprange2), 20)) 

p = np.hstack([np.arange(2, 4.6, 0.5), np.arange(5, 9.1, 1.0)])

contours = self.ax.contourf(x, p, ys, levels=levels, extend='both', cmap='gist_earth_r')
contours = self.ax.contour(x, p, ys, levels=levels, extend='both', cmap='gist_earth_r')
self.ax.set_xlabel('optical energy (eV)')
self.ax.set_ylabel('electron energy (keV)')

self.ax.set_title('Aixtron sample cathodoluminescence')
self.ax.set_xlim([1.6,4])

ax2 = self.ax.twiny()
def tick_function(p):
    return 10.46*(p**1.68)
ax2.set_xlim(ax.get_ylim())
new_tick_locations = np.arange(2, 9, .5)
ax2.set_xticks(new_tick_locations)
ax2.set_yticklabels(tick_function(new_tick_locations))
ax2.set_ylabel('electron penetration depth (nm)')
"""


plot_commands = {'Lines':line_plot_command, 'Contours':contour_plot_command}

class Handler:
    ## == initialization == 
    def __init__(self): #{{{
        self.lockTreeViewEvents = False
        np.seterr(all='ignore')

        ## Plotting initialization
        self.fig = matplotlib.figure.Figure(figsize=(8,8), dpi=96, facecolor='#eeeeee', tight_layout=1) 
        # (figure is static, axes clear on every replot)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(300,300)
        self.toolbar = matplotlib.backends.backend_gtk3.NavigationToolbar2GTK3(self.canvas, w('box4').get_parent_window())

        self.xlim, self.ylim = None, None
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
        self.dat_file_cache = {}

        ## TreeStore and ListStore initialization #TODO into separate routine?
        self.tsFiles = Gtk.TreeStore(str,          Pixbuf,   str,      Pixbuf,            int,        int,             str)
        self.treeStoreColumns =     {'filepath':0, 'icon':1, 'name':2, 'plotstyleicon':3, 'column':4, 'spreadsheet':5, 'rowtype':6}
        self.dummy_treestore_row = [None for x in self.treeStoreColumns.keys()]

        treeViewCol0 = Gtk.TreeViewColumn(' ')        # Create a TreeViewColumn
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
        w('txt_rc').get_buffer().set_text(line_plot_command)
        w('txt_rc').modify_font(Pango.FontDescription("monospace 10"))


        ## Add the data cursor by default  # TODO - make this work
        #cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)


        #}}}
    ## === FILE HANDLING ===
    def is_branch(self,filename): # {{{
        try:

            result = stat.S_ISDIR(os.stat(filename).st_mode)
            #print('testing ', filename, 'result=', result)
            return result
        except FileNotFoundError: ## this may be e.g. due to a broken symlink
            print('warning: error occured reading ', filename)
            return False
        # }}}
    def row_type_from_fullpath(self, fullpath):# {{{
        """
        Known row types:

            #Type                   row_is_leaf row_can_plot    row_icon-TODO
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

        if self.is_branch(fullpath):
            return 'dir'
        elif fullpath.lower().endswith('.xls'):
            ## TODO XLS support : determine if single spreadsheet, and/or if spreadsheet(s) contain single column
            return 'xlsfile'
        elif fullpath.lower().endswith('.opj'):
            return 'opjfile'
        elif any(fullpath.lower().endswith(try_ending) for try_ending in ('.csv', '.tsv', '.dat', '.txt', '.asc')):
            try:
                ## Note: column number is incorrectly determined if header is longer than sizehint, but 10kB should be enough
                data_array, header, parameters = robust_csv_parser.loadtxt(fullpath, sizehint=SIZELIMIT_FOR_HEADER) 
                if len(header)<=2: return 'csvtwocolumn' 
                else: return 'csvmulticolumn'
            except (IOError, RuntimeError):    # This error is usually returned for directories and non-data files
                return 'unknown'
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
    def origin_parse_or_cache(self, filepath):# {{{
        ## FIXME update cache on file change!
        if not filepath in self.opj_file_cache.keys()  or  os.stat(filepath).st_mtime > self.opj_file_cache[filepath]['LastLoadTime']:
            import liborigin
            FileContent = liborigin.parseOriginFile(filepath)
            LastLoadTime = os.stat(filepath).st_mtime
            self.opj_file_cache[filepath] =  {'LastLoadTime':LastLoadTime, 'FileContent':FileContent}
        return self.opj_file_cache[filepath]
        # }}}
    def dat_parse_or_cache(self, filepath):# {{{
        if not filepath in self.dat_file_cache.keys()  or  os.stat(filepath).st_mtime > self.dat_file_cache[filepath]['LastLoadTime']:
            FileContent  = robust_csv_parser.loadtxt(filepath, sizehint=SIZELIMIT_FOR_DATA)
            LastLoadTime = os.stat(filepath).st_mtime
            self.dat_file_cache[filepath] = {'LastLoadTime':LastLoadTime, 'FileContent':FileContent}
        return self.dat_file_cache[filepath]['FileContent']
        # }}}
    def decode_origin_label(self, bb, splitrows=False): # {{{
        bb = bb.decode('utf-8', errors='ignore').replace('\r', '').strip()
        bb = bb.replace('\\-', '_')     ## this is the lower index - todo: use latex notation?
        for asc,greek in zip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'αβγδεζηθιjκλμνοπρςστυφχξψωΑΒΓΔΕΖΗΘΙJΚΛΜΝΟΠQΡΣΤΥΦΧΞΨΩ'):
            bb = bb.replace('\\g(%s)' % asc, greek)
        if not splitrows:   return bb.replace('\n', ' ')
        else:               return bb.split('\n')
    # }}}
    def populateTreeStore(self, treeStore, parent_row=None, reset_path=None):# {{{
        ## without any parent specified, rows will be added to the root (i.e. very left) of the TreeView, 
        ## otherwise they will become childs thereof

        # Note: We use the concept of "branches" and "leaves", which is similar to "folders" and "files".
        # However, it is not the same, since a file may contain more data columns, thus being a branch. 
        # Flattening is a user-friendly way of viewing the tree, which may reduce clicking. If a branch 
        # contains exactly one leaf, it will be treated as a leaf itself. 
        def semirecursive_flattening_file_search(trypath, indent):
            ## Note: Returning 0 means the branch is empty, returning 2 means it contains two or more objects
            ## Todo: use the same procedure also for e.g. columns within files

            ## Read what is found under trypath: (TODO generalize to more than just filesystem!)
            leaves   = [f for f in os.listdir(trypath) if (not self.is_branch(os.path.join(trypath,f)) 
                and (fileFilterString == '' or re.findall(fileFilterString, f)))]    
            branches = [f for f in os.listdir(trypath) if (self.is_branch(os.path.join(trypath,f))     
                and (dirFilterString == '' or re.findall(dirFilterString, os.path.basename(f))))]
            ## todo: hide also leaves that could not be loaded as data

            if len(leaves) >= 2: return 2       #  has 2 or more leaves, cannot be collapsed, just quit

            recbs = []
            complex_branch_name = None
            for b in branches:
                recb = semirecursive_flattening_file_search(os.path.join(trypath,b), indent+'·   ')
                if recb!=0:
                    recbs.append(recb); complex_branch_name = b
                if len(recbs)>=2:           # contains 2 or more branches, cannot be collapsed
                    return 2

            if len(recbs) == 0:
                if len(leaves) == 0: return 0   # branch effectively empty (contains nothing that passes our filters)
                if len(leaves) == 1: return os.path.join(trypath, leaves[0]) # has one leaf, can collapse
            if len(recbs) == 1:
                if len(leaves) == 0:
                    if recbs[0] == 2:           # contains one branch only with more objects, can collapse this
                        return os.path.join(trypath, complex_branch_name)   
                    else:                       # contains one already collapsed branch, collapse further
                        return recbs[0] 
                if len(leaves) == 1: return 2   # contains more objects, so cannot be collapsed

        if parent_row is None:
            if reset_path is not None:
                basepath = reset_path
            else:
                if self.row_prop(self.tsFiles.get_iter_first(), 'rowtype') == 'updir':
                    basepath = self.row_prop(self.tsFiles.get_iter_first(), 'filepath')
                else:
                    raise AttributeError('Specify either parent_row, reset_path, or ensure the first row is of "updir" type')
            w('window1').set_title('PlotCommander: %s' % basepath)

            ## On startup, or when the 'updir' node is selected, we update the whole tree. 
            ## Initially, it has to be cleared of all rows. 
            ## During this operation, its selection will change, so we lock the plotting from being updated so that it is fast.
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
            raise AttributeError()

        ## Prepare the lists of paths, column numbers and spreadsheet numbers to be added
        parentrowtype = self.row_prop(parent_row, 'rowtype') if parent_row else 'dir'
        assert not self.rowtype_is_leaf(parentrowtype)

        if parentrowtype == 'dir':             ## Populate a directory with files/subdirs
            ## Get the directory contents and sort it alphabetically

            fileFilterString = w('enFileFilter').get_text().strip() 
            dirFilterString = w('enDirFilter').get_text().strip() 

            if not w('chk_FlattenFolders').get_active():
                leaves   = sorted([os.path.join(basepath,f) for f in os.listdir(basepath)  if (not self.is_branch(os.path.join(basepath,f)) 
                    and (fileFilterString == '' or re.findall(fileFilterString, f)))], key=sort_alpha_numeric.split_alpha_numeric_lowercase)    
                branches = sorted([os.path.join(basepath,f) for f in os.listdir(basepath)  if (self.is_branch(os.path.join(basepath,f))     
                    and (dirFilterString == '' or re.findall(dirFilterString, os.path.basename(f))))], key=sort_alpha_numeric.split_alpha_numeric_lowercase)
                filenames = branches + leaves
            else:
                filenames = []
                leaves   = sorted([os.path.join(basepath,f) for f in os.listdir(basepath)  if (not self.is_branch(os.path.join(basepath,f)) 
                    and (fileFilterString == '' or re.findall(fileFilterString, f)))], key=sort_alpha_numeric.split_alpha_numeric_lowercase)    
                branches = sorted([os.path.join(basepath,f) for f in os.listdir(basepath)  if (self.is_branch(os.path.join(basepath,f))     
                    and (dirFilterString == '' or re.findall(dirFilterString, os.path.basename(f))))], key=sort_alpha_numeric.split_alpha_numeric_lowercase)
                for b in branches:
                    recb = semirecursive_flattening_file_search(os.path.join(basepath,b), '')
                    if recb == 2:
                        filenames.append(b)
                    elif recb != 0:
                        filenames.append(recb)
                filenames += leaves

            itemFullNames = filenames #[os.path.join(basepath, filename) for filename in filenames]    # add the full path
            itemShowNames = [fn[len(basepath)+1:] for fn in filenames]                 # only file name without path will be shown
            columnNumbers = [None] * len(itemFullNames)    # obviously files/subdirs are assigned no column number
            spreadNumbers = [None] * len(itemFullNames)    # nor they are assigned any spreadsheet number
            rowTypes      = [self.row_type_from_fullpath(f) for f in itemFullNames]
        elif parentrowtype == 'csvmulticolumn':
            ## Note: Multicolumn means at least 3 columns (i.e. x-column and two or more y-columns)
            txt = self.dat_parse_or_cache(basepath)
            data_array, header, parameters = txt 
            columnFilterString = w('enColFilter').get_text().strip()   #XXX XXX 
            #columnFilterString = 'gamma|fermi'
            columnNumbers, header = zip(*[n for n in enumerate(header) if re.findall(columnFilterString, n[1])]) ## filter the columns
            #FIXME File "/home/dominecf/p/plotcommander/plotcommander.py", line 303, in populateTreeStore
                #columnNumbers, header = zip(*[n for n in enumerate(header) if re.findall(columnFilterString, n[1])]) ## filter the columns
            #ValueError: not enough values to unpack (expected 2, got 0)
            itemFullNames = [basepath] * len(header)    # all columns are from one file
            itemShowNames = header                      # column numbers are either in file header, or auto-generated
            spreadNumbers = [None] * len(header)        # there are no spreadsheets in CSV files
            rowTypes      = ['csvcolumn'] * len(header)
        elif parentrowtype == 'opjfile':
            opj = self.origin_parse_or_cache(basepath)
            ## Add "graphs" - which show the selected columns in presentation-ready format
            ## todo: support for multiple opjlayers also here
            ## todo: take into account this field with useful data:   ["spreads"].columns[3].comment = b"PL Intensity^M [arb. units]^M 110A 10%"
            def generate_graph_annotation(graph): 
                layerNumber = 0  ## Fixme support for multiple opjlayers:    ["graphs"][1].layers[0].curves[3].xColumnName
                try:
                    legend_box = self.decode_origin_label(graph.layers[0].legend.text, splitrows=True)
                except IndexError:
                    legend_box = ''
                comment = ""
                for legendline in legend_box:  ## the legend may have format as such: ['\l(1) 50B', '\l(2) 48B', ...], needs to be pre-formatted:
                    newline = re.sub(r'\\l\(\d\)\s', '', legendline) 
                    if newline == legendline: comment += newline + ' '
                return comment
            itemShowNames = ['%s; name: %s; label: %s' % (self.decode_origin_label(graph.name), self.decode_origin_label(graph.label), 
                    generate_graph_annotation(graph)) for graph in opj['graphs']]
            itemFullNames = [basepath] * len(itemShowNames)    # all columns are from one file
            columnNumbers = [None] * len(itemShowNames)
            spreadNumbers = list(range(len(itemShowNames)))  
            rowTypes      = ['opjgraph'] * len(itemShowNames)

            ## Add "columns" - which enable to access all data in the file, including those not used in "graphs"
            #for spread in opj['spreads']:
                #print(spread.label, self.decode_origin_label(spread.label))
            itemShowNames = itemShowNames + ['%s "%s"' % (self.decode_origin_label(spread.name), self.decode_origin_label(spread.label)) 
                    for spread in opj['spreads']]
            itemFullNames = itemFullNames + [basepath] * len(itemShowNames)    # all columns are from one file
            columnNumbers = columnNumbers + [None] * len(itemShowNames)
            spreadNumbers = spreadNumbers + list(range(len(itemShowNames)))  
            rowTypes      = rowTypes      + ['opjspread'] * len(itemShowNames)
        elif parentrowtype == 'opjspread':
            opj = self.origin_parse_or_cache(basepath)
            parent_spreadsheet = self.row_prop(parent_row, 'spreadsheet')
            itemShowNames = [self.decode_origin_label(column.name)+" "+self.decode_origin_label(column.comment) for column in 
                    opj['spreads'][parent_spreadsheet].columns]
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
            #print("opj['graphs'][parent_graph].layers[layerNumber].curves", curves, 'with names=', [curve.dataName for curve in curves])
            legend_box = self.decode_origin_label(opj['graphs'][parent_graph].layers[layerNumber].legend.text, splitrows=True)
            legends = []
            for legendline in legend_box:  ## the legend may have format as such: ['\l(1) 50B', '\l(2) 48B', ...], needs to be pre-formatted:
                newline = re.sub(r'\\l\(\d\)\s', '', legendline) 
                if newline != legendline:   legends.append(newline)
            legends = legends[:len(curves)] + (['']*(len(curves)-len(legends))) ## trim or extend the legends to match the curves

            itemShowNames, itemFullNames, columnNumbers, spreadNumbers = [], [], [], []
            for curve, legend in zip(curves, legends):
                ## FIXME add support for xColumn different than the first one in Spreadsheet, also here
                #print("curve t xCol yCol:", curve.dataName.self.decode_origin_label('utf-8'), 
                        #curve.xColumnName.self.decode_origin_label('utf-8'), curve.yColumnName.self.decode_origin_label('utf-8'))
                #print([spread.name for spread in opj['spreads']], (curve.dataName[2:]))

                ## Seek the corresponding spreadsheet and column by their name
                spreadsheet_index = [spread.name for spread in opj['spreads']].index(curve.dataName[2:])
                spread = opj['spreads'][spreadsheet_index]
                y_column_index = [column.name for column in spread.columns].index(curve.yColumnName)
                x_column_index = [column.name for column in spread.columns].index(curve.xColumnName)
                #print(curve.dataName[2:].self.decode_origin_label('utf-8'), spreadsheet_index, 
                        #curve.yColumnName.self.decode_origin_label('utf-8'), y_column_index)

                itemShowNames.append('%s -> spread %s: column %s (%s)' %  
                        (legend, self.decode_origin_label(spread.name), 
                                self.decode_origin_label(spread.columns[y_column_index].name), 
                                self.decode_origin_label(spread.columns[y_column_index].comment))) ### TODO we write "against" but 
                itemFullNames.append(basepath)          # all columns are from one file
                columnNumbers.append(y_column_index)  
                spreadNumbers.append(spreadsheet_index)
            rowTypes      = ['opjcolumn'] * len(itemShowNames) ## TODO or introduce opjgraphcurve ?
        else:
            warnings.warn('Not prepared yet to show listings of this file: %s' % parentrowtype)
            return


        ## Go through all items and populate the node
        for itemFullName, itemShowName, columnNumber, spreadNumber, rowtype in \
                zip(itemFullNames, itemShowNames, columnNumbers, spreadNumbers, rowTypes):
            plotstyleIcon = Pixbuf.new(Colorspace.RGB, True, 8, 10, 10)
            plotstyleIcon.fill(0xffffffff)
            if rowtype != 'unknown' or w('chk_ShowAllFiles').get_active():
                currentIter = treeStore.append(parent_row, 
                        [itemFullName, self.rowtype_icon(rowtype), itemShowName, plotstyleIcon, columnNumber, spreadNumber, rowtype])
            if not self.rowtype_is_leaf(rowtype): ## TODO row---> parentrowtype
                treeStore.append(currentIter, self.dummy_treestore_row)     # shows the "unpacking arrow" left of the item
        # }}}


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
        self.fig.clf()
        self.ax = self.fig.add_subplot(111) 
        self.ax.callbacks.connect('xlim_changed', self.on_xlims_change)
        self.ax.callbacks.connect('ylim_changed', self.on_ylims_change)

        ## TODO: this may enable better handling of axes, but needs to make compatible with the object model of figure.Figure 
        #        self.ax = host_subplot(111, figure=self.fig.gcf() ) 

        def recursive_clear_icon(treeIter):
            while treeIter != None: 
                iterpixbuf = self.tsFiles.get_value(treeIter, 3)
                if iterpixbuf: iterpixbuf.fill(self.array2rgbhex([.5,.5,1], alpha=0)) ## some nodes may have pixbuf set to None
                recursive_clear_icon(self.tsFiles.iter_children(treeIter))
                treeIter=self.tsFiles.iter_next(treeIter)
        recursive_clear_icon(self.tsFiles.get_iter_first())
        w('treeview1').queue_draw()
        # }}}
    def safe_np_array(self, x,y): ## converts two lists to 2 numpy array; if float() fails when processing any (x,y) row, leave it out {{{
        if len(x)>2 and x[-2]>x[-1]*1e6: x=x[:-1]       ## (fixme) the last row from liborigin is sometimes erroneous zero
        if len(x) < len(y): y = y[0:len(x)]             ## in any case, match the length of x- and y-data
        if len(y) < len(x): x = x[0:len(y)] 
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
        return x, y 
    # }}}
    def load_row_data(self, row):# {{{
        """ loads all relevant data for a given treestore row, and returns: x, y, label, parameters, xlabel, ylabel

        Plotting is "on-the-fly", i.e., program does not store any data (except DAT/OPJ file cache) and loads them 
        from disk upon every (re)plot. TODO reload the cache on file change!
        """
        ## Load the data
        rowfilepath = self.row_prop(row, 'filepath')
        rowtype     = self.row_prop(row, 'rowtype')
        rowxcolumn  = 0 ## TODO allow ordinate also on >0th column 
        rowycolumn  = self.row_prop(row, 'column')
        rowsheet    = self.row_prop(row, 'spreadsheet')
        if  rowtype == 'opjcolumn':
            opj = self.origin_parse_or_cache(rowfilepath)
            # TODO: what does opj['spreads'][3].multisheet mean?
            x, y = [opj['spreads'][rowsheet].columns[c].data for c in [rowxcolumn, rowycolumn]]
            x, y = self.safe_np_array(x, y)
            xlabel, ylabel = [self.decode_origin_label(opj['spreads'][rowsheet].columns[c].name) for c in [rowxcolumn, rowycolumn]] 
            parameters = {} ## todo: is it possible to load parameters from origin column?
            descriptor = rowfilepath+" "+ylabel+" "+self.decode_origin_label(opj['spreads'][rowsheet].columns[rowycolumn].comment) ## FIXME XXX
            return x, y, descriptor, parameters, xlabel, ylabel
        elif rowtype in ('csvtwocolumn', 'csvcolumn'): 
            data_array, header, parameters = self.dat_parse_or_cache(rowfilepath)
            if rowtype == 'csvtwocolumn': 
                rowxcolumn, rowycolumn = 0, 1
                ## in fact, file denoted as "csvtwocolumn" may have only one column, in such a case generate simple integer x-axis numbering
                if len(header) == 1: 
                    data_array = np.vstack([np.arange(len(data_array)), data_array.T]).T # 
                    header     = ['point number'] + header

            ## TODO consider also parameters in the file! 
            descriptor = rowfilepath +" "+header[rowycolumn] 
            return data_array.T[rowxcolumn], data_array.T[rowycolumn], descriptor, parameters, header[rowxcolumn], header[rowycolumn] 

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
    def dedup_keys_values(self, keyvalue_strings, output_strings=True, output_removed=False):# {{{
        """ Seeks for key=value pairs that are shared with among all strings in the list, and removes them if found """
        def try_float_value(tup): 
            """ Whenever possible, safely convert second tuple items (i.e. values) to float """
            if len(tup)==1:             return tup
            elif len(tup)==2:
                try:                    return (tup[0], float(tup[1]))
                except:                 return tup
        def all_to_string(tup): return [str(v) for v in tup]
        ## File name may be interesting as curve label, but not its extension -> filter it out
        keyvalue_strings = [re.sub('\.[a-zA-Z][\w]?[\w]?$', '', kvstring) for kvstring in keyvalue_strings]

        ## Split names into "key=value" chunks and  then into ("key"="value") tuples
        keyvaluelists = []
        for keyvalue_string in keyvalue_strings: 
            #print("keyvalue_strings", keyvalue_strings) ## TODO clean up debugging leftovers
            chunklist = re.split('[_ /]', keyvalue_string) 
            #print("    chunklist", chunklist)
            keyvaluelist = [try_float_value(re.split('=', chunk.replace('~', ' '))) for chunk in chunklist] 
            #print("   -> keyvaluelist", keyvaluelist)
            keyvaluelists.append(keyvaluelist)
        ## If identical ("key"="value") tuple found everywhere, remove it 
        ## FIXME: removes also keys that are contained deep in the names of common upper directory; in such a case should 
        ## eliminate the common directory name first
        removedkvlist = []
        for keyvaluelist in keyvaluelists.copy(): 
            #print("KEYVALUELIST ---------- ", keyvaluelist)
            for keyvalue in keyvaluelist.copy():
                if all([(keyvalue in testkeyvaluelist) for testkeyvaluelist in keyvaluelists]):
                    if keyvalue == '70mm': print("REMOVING", keyvalue , "it was found in all" , keyvaluelists )
                    for keyvaluelist2 in keyvaluelists:
                        keyvaluelist2.remove(keyvalue)
                    removedkvlist.append(keyvalue)

        ## By default, return simple flat list of strings, otherwise a nested [[(key,value), ...]] structure
        if output_strings:
            keyvaluelists = [' '.join(['='.join(all_to_string(kvpair)) for kvpair in keyvaluelist]).strip() for keyvaluelist in keyvaluelists]
            removedkvlist = ['='.join(all_to_string(kvpair)).strip() for kvpair in removedkvlist]

        if output_removed:      ## Optionally, output also the parameters that are shared among all files
            return keyvaluelists, removedkvlist
        else:
            return keyvaluelists
# }}}
    def plot_all_sel_records(self):# {{{

        ## Setting persistent view is somewhat kafkaesque with matplotlib. 
        ## self.xlim        remembers the correct view from the last GUI resize , but
        ## ax.get_xlim      from the start of this method returns the wrong (autoscaled) limits, why?
        if not w('chk_autoscale_x').get_active() and self.xlim: self.ax.set_xlim(self.xlim)
        if not w('chk_autoscale_y').get_active() and self.ylim: self.ax.set_ylim(self.ylim)

        ## Load all row data
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if len(pathlist) == 0: return
        error_counter = 0
        row_data = []
        row_labels = []
        plotted_paths = []
        for path in pathlist:
            try:
                row_data.append(self.load_row_data(self.tsFiles.get_iter(path)))
                plotted_paths.append(path)
            except (RuntimeError, ValueError):
                traceback.print_exc()
                error_counter += 1
        w('statusbar1').push(0, ('%d records loaded' % len(pathlist)) + ('with %d errors' % error_counter) if error_counter else '')
        if row_data == []: return False
        xs, ys, labels_orig, params, xlabels, ylabels = zip(*row_data)       
        labels, sharedlabels = self.dedup_keys_values(labels_orig, output_removed=True)
        #print('LABELS', labels, 'sharedlabels', sharedlabels)

        #for n,v in zip('xs, ys, labels, params, xlabels, ylabels'.split(), [xs, ys, labels, params, xlabels, ylabels]):
            #print(n,v)
        ##
        ## TODO: Once files are correctly named:
        ## additionally check if there is exactly one column in the 'params' table that differs among files:       label="%s=%s" % (labelkey, labelval)
        ## If it is, set its name and value to:  zs and zlabels   variables for correct plotting contour maps
        ## ?? If there is none, or too many, the curves will be labeled just by their column label found in the header. 
        ## TODO allow also to name the curves by the file name, if the column names do not exist or are all the same!

        ## Generate the color palette for curves
        color_pre_map = np.linspace(0.05, .95, len(plotted_paths)+1)[:-1]
        colors = matplotlib.cm.gist_rainbow(color_pre_map*.5 + np.sin(color_pre_map*np.pi/2)**2*.5)
        for path, color_from_palette in zip(plotted_paths, colors):
            ## If no exception occured during loading, colour the icon according to the line colour
            icon = self.row_prop(self.tsFiles.get_iter(path), 'plotstyleicon')
            if icon: icon.fill(self.array2rgbhex(color_from_palette))
            plotted_paths.append(path) ## TODO: this is really confusing, since we have been iterating over plotted_paths!

        ## TODO: decide what is the distinguishing parameter for the given set of rows ---> <str> labelkey, <labelvals
        # 1) (almost) all curves should have it defined
        # 2) it should differ among (almost) all curves 
        # 3) it may be in the params dict, or in the filename (for csvtwocolumn), or in the header of csvcolumn, opjcolumn etc.


        #print("self.ax.axis", self.ax.axis())
        ## Plot all curves sequentially
        plot_cmd_buffer = w('txt_rc').get_buffer() 
        plot_command = plot_cmd_buffer.get_text(plot_cmd_buffer.get_start_iter(), plot_cmd_buffer.get_end_iter(), 
                include_hidden_chars=True)
        #print("BEFORE COMMAND")
        #print(row_data)
        if plot_command.strip() == '': return
        tosave=[]
        init_time = time.time()
        #np = numpy
        def dedup(l): return list(dict.fromkeys(l[::-1]))[::-1] ## deduplicates items, preserves order of first occurence
        exec_env = {'np':np, 'sc':sc, 'matplotlib':matplotlib, 'cm':matplotlib.cm, 'ax':self.ax, 'fig': self.fig, 
                'xs':np.array(xs), 'ys':np.array(ys), 'labels':labels, 'sharedlabels':sharedlabels, 'params':np.array(params), 'xlabels':xlabels,  'ylabels':ylabels,  
                'xlabelsdedup':', '.join(dedup(xlabels))[:100],  'ylabelsdedup':', '.join(dedup(ylabels))[:100], 
                'colors':colors, 'tosave':tosave, 'labels_orig':labels_orig}
        #print(exec_env)

        #self.fig.clf() ## clear figure
        try:
            exec(plot_command, exec_env)
            #print("JUST AFTER COMMAND")
        except SyntaxError:
            #print("SYNTAX ERROR:")
            traceback.print_exc() ## TODO locate the error
        except:
            #print("SOME ERROR")
            traceback.print_exc() ## TODO locate the error

        print('Plotting script finished in {:.3f} s'.format(time.time()-init_time)); init_time = time.time()
        if tosave != []: print('Exported image files in the `tosave` list:', tosave)
        try: 
            for savefilename in list(tosave):
                self.fig.savefig(savefilename)
                print("Plotcommander: saving output to:", savefilename)
        except IOError as e:
            print("Plotcommander: saving output failed with", e)


        #print("AFTER COMMAND")
            #code = compile(plot_command, "somefile.py", 'exec') TODO
            #exec(code, global_vars, local_vars)
        #else:
            #plot_command = default_plot_command
            #plot_cmd_buffer.set_text(default_plot_command)


        #self.ax.legend(loc="best")
        self.ax.grid(True)
        self.ax.set_xscale('log' if w('chk_xlogarithmic').get_active() else 'linear') 
        self.ax.set_yscale('log' if w('chk_ylogarithmic').get_active() else 'linear')

        #print(" - relim - ")
        #self.ax.relim() ## If relim enabled, logarithmic axes scale wrong, i.e. from (6.7370464889520478e-316, 4.0007331215613123e+18)
        #print(" - autoscale - ")
        #self.ax.autoscale_view() # 	Autoscale the view limits using the data limits.
        #print(" - draw - ")

        #cursor = Cursor(self.ax, color='red', linewidth=.5)  ## FIXME http://blog.yjl.im/2009/10/blit-cursor-in-matplotlib.html
        self.canvas.draw()

        print('Drawing finished in {:.3f} s'.format(time.time()-init_time))
        return True

        """
        xlims_changed from  (4.6147009455810979, 3650.4430782521085)
                      to    (-128.203125, 2829.765625)
        xlims_changed from  (-128.203125, 2829.765625)
                      to    (4.6147009455810979, 3650.4430782521085)
         - relim - 
         - autoscale - 
        xlims_changed from  (4.6147009455810979, 3650.4430782521085)
                      to    (4.6147009455810979, 3650.4430782521085)            <-------- OK, but why?
         - draw - 



        xlims_changed from  (8.0705914746898669e-316, 90154482521167872.0)
                      to    (-128.203125, 2829.765625)
        xlims_changed from  (-128.203125, 2829.765625)
                      to    (4.6147009455810979, 3650.4430782521085)
         - DISABLED relim - 
         - autoscale - 
        xlims_changed from  (4.6147009455810979, 3650.4430782521085)
                      to    (6.7370464889520478e-316, 4.0007331215613123e+18)           <---------- wrong!
         - draw - 


        xlims_changed from  None
                      to    (-128.203125, 2829.765625)
        xlims_changed from  (-128.203125, 2829.765625)
                      to    (4.6147009455810979, 3650.4430782521085)
         - DISABLED relim - 
         - DISABLED autoscale - 
         - draw -                                           <--------------------- and everything is OK

        """

        # }}}
    def on_xlims_change(self, axes): # {{{
        self.xlim = axes.get_xlim() ## FIXME dirty hack: Needs some elegant solution in the future
    def on_ylims_change(self, axes): 
        self.ylim = axes.get_ylim() ## dtto
        #print("xlims_changed from ", self.ylim)
        #print("              to   ", self.ylim)
    # }}}

    ## == FILE AND DATA UTILITIES ==
    def row_prop(self, row, prop):# {{{ ## get rid of this
        return self.tsFiles.get_value(row, self.treeStoreColumns[prop])
        # }}}
    def remember_treeView_expanded_rows(self, treeStore, treeView):    # {{{
        ## returns a list of paths of expanded files/directories
        def recurse_treestore(treeIter):
            while treeIter != None: 
                if w('treeview1').row_expanded(treeStore.get_path(treeIter)):
                    expanded_row_names.append(treeStore.get_value(treeIter, 0))      # get the full path of the position
                recurse_treestore(treeStore.iter_children(treeIter))
                treeIter=treeStore.iter_next(treeIter)
        treeIter = treeStore.get_iter_first()
        expanded_row_names = [treeStore.get_value(treeIter, 0)] ## remember that also the "root" directory of the view is unpacked
        recurse_treestore(treeIter)
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
                if self.tsFiles.get_value(treeIter, 0) in expanded_row_names[::-1]:
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
                    self.lockTreeViewEvents = True
                    w('treeview1').get_selection().select_path(self.tsFiles.get_path(treeIter))
                    self.lockTreeViewEvents = False
                recursive_select_rows(self.tsFiles.iter_children(treeIter))
                treeIter=self.tsFiles.iter_next(treeIter)
        recursive_select_rows(self.tsFiles.get_iter_first())
        self.plot_all_sel_records() # TODO needed here?
        # }}}
    def on_btn_EditSelFiles_clicked(self, dummy):    ## code taken from self.plot_all_sel_records(){{{
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if len(pathlist) == 0: return
        try:
            import subprocess
            print(external_editor_command, [self.row_prop(self.tsFiles.get_iter(path), 'filepath') for path in pathlist])
            subprocess.Popen(list(external_editor_command) + [self.row_prop(self.tsFiles.get_iter(path), 'filepath') for path in pathlist])
        except Exception as e:
            print(e)
    # }}}
    def on_btn_TrashSelFiles_clicked(self, dummy): # {{{
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if len(pathlist) == 0: return
        try:
            print('TODO on_btn_TrashSelFiles_clicked: stub')
            ## TODO 
            #p = pathlib.Path("temp/")
            #p.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(e)
    # }}}

         

    ## == USER INTERFACE HANDLERS ==
    ## == Python plotting script ==
    def on_btn_plotrc_save_clicked(self, *args):# {{{
        rc_filename = self.relevant_rc_filename() or self.possible_rc_filenames()[0]
        with open(rc_filename, 'w') as rcfile:
            rcfile.write(self.plotcommand_get_text())
    """
    if radio changes to some defaultcommand
                    ---> change to selected command
    if radio changes to rcfile
        if relevant rcfile exists
                    ---> change to selected command ( LOAD rcfile command)
                    ---> then REPLOT
        if rcfile does not exist
                    ---> EMPTy txtbox 
        if nothing selected
                    ---> EMPTy txtbox 
    if selection changes 
        if relevant rcfile exists   
                    ---> CHANGE radio TO RCFILE
                    ---> change to selected command ( LOAD rcfile command) (automatic event handler?)
        if rcfile does not exist
                    ---> CHANGE radio TO DEFAULT
        if nothing selected
                    --->

    ---> then always REPLOT
    """
    # }}}

    def on_btn_ExtScriptEditor_clicked(self, dummy): # {{{
        try:
            import subprocess
            rc_filename = self.relevant_rc_filename() or self.possible_rc_filenames()[0]
            print("Opening external editor:", external_editor_command, [rc_filename])
            subprocess.Popen(list(external_editor_command) + [rc_filename])
        except Exception as e:
            print(e)# }}}

    def btn_exteditor_clicked_cb(self, sender):# {{{
        ## TODO launch selected editor, ask for the program if undefined
        print('stub',sender)
    # }}}
    def possible_rc_filenames(self):# {{{
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if pathlist:
            firstselfilenamepath = self.row_prop(self.tsFiles.get_iter(pathlist[0]), 'filepath')
            firstselfilepath, firstselfilename = os.path.dirname(firstselfilenamepath), os.path.basename(firstselfilenamepath) 
            testrcfilenamepath1 = os.path.join(firstselfilepath, 'plotrc_%s.py' % firstselfilename)
            testrcfilenamepath2 = os.path.join(firstselfilepath, 'plotrc.py') 
            return (testrcfilenamepath1, testrcfilenamepath2)
        else:
            return None

    def relevant_rc_filename(self):
        prf = self.possible_rc_filenames()
        if prf: 
            rc_filename = prf[0] if os.path.isfile(prf[0]) else prf[1] if os.path.isfile(prf[1]) else None
            return rc_filename
        else:
            return None

    def load_plotcommand_from_rcfile(self):
        rc_filename = self.relevant_rc_filename()
        if rc_filename:
            with open(rc_filename) as rcfile:
                return rcfile.read()
        else:
            return ''

    def update_plotcommand_from_rcfile(self, allow_overwrite_by_empty=True):
        plotcommand =  self.load_plotcommand_from_rcfile()
        if plotcommand or allow_overwrite_by_empty:
            w('txt_rc').get_buffer().set_text(plotcommand)

    def plotcommand_get_text(self):
        buf = w('txt_rc').get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), include_hidden_chars=True)
    def plotcommand_set_text(self, text):
        buf = w('txt_rc').get_buffer()
        buf.set_text(text)# }}}
    def on_plotcommand_toggled(self, *args):# {{{
        radiobutton = args[0]
        
        w('chk_xlogarithmic').set_active(False)
        if radiobutton is w('rad_plotstyle_rc'):
            if radiobutton.get_active():        ## selecting action
                self.update_plotcommand_from_rcfile(allow_overwrite_by_empty=True)
            else:
                pass ## todo - ask whether to save the command file, if changed
        else:
            if radiobutton.get_active():        ## selecting action
                self.plotcommand_set_text(plot_commands[radiobutton.get_label().strip()])        
            else:                               ## deselecting action
                plot_commands[radiobutton.get_label().strip()] = self.plotcommand_get_text()

        if radiobutton.get_active():        ## selecting action
            ## Update the graphical presentation
            self.plot_reset()               ## first delete the curves, to hide (also) unselected plots
            self.plot_all_sel_records()     ## then show the selected ones

    # }}}
    def on_btn_plotrc_replot_clicked(self, *args):# {{{
        self.plot_reset() ## clear figure
        self.update_plotcommand_from_rcfile(allow_overwrite_by_empty=False)
        # check if textbox differs from the existing file (i.e. had been edited...); if so, auto-save it
        self.plot_all_sel_records()
    # }}}
    def on_chk_xlogarithmic_toggled(self, sender):# {{{
        self.fig.gca().set_xscale('log' if w('chk_xlogarithmic').get_active() else 'linear')
        self.canvas.draw()
    def on_chk_ylogarithmic_toggled(self, sender):
        self.fig.gca().set_yscale('log' if w('chk_ylogarithmic').get_active() else 'linear')
        self.canvas.draw()
    # }}}
    def possible_rc_filenames(self):# {{{
        (model, pathlist) = w('treeview1').get_selection().get_selected_rows()
        if pathlist:
            firstselfilenamepath = self.row_prop(self.tsFiles.get_iter(pathlist[0]), 'filepath')
            firstselfilepath, firstselfilename = os.path.dirname(firstselfilenamepath), os.path.basename(firstselfilenamepath) 
            testrcfilenamepath1 = os.path.join(firstselfilepath, 'plotrc_%s.py' % firstselfilename)
            testrcfilenamepath2 = os.path.join(firstselfilepath, 'plotrc.py') 
            return (testrcfilenamepath1, testrcfilenamepath2)
        else:
            return None
# }}}
    def relevant_rc_filename(self):# {{{
        prf = self.possible_rc_filenames()
        if prf: 
            rc_filename = prf[0] if os.path.isfile(prf[0]) else prf[1] if os.path.isfile(prf[1]) else None
            return rc_filename
        else:
            return None
# }}}
    def load_plotcommand_from_rcfile(self):# {{{
        rc_filename = self.relevant_rc_filename()
        if rc_filename:
            with open(rc_filename) as rcfile:
                return rcfile.read()
        else:
            return ''

    def update_plotcommand_from_rcfile(self, allow_overwrite_by_empty=True):
        plotcommand =  self.load_plotcommand_from_rcfile()
        if plotcommand or allow_overwrite_by_empty:
            w('txt_rc').get_buffer().set_text(plotcommand)

    def plotcommand_get_text(self):
        buf = w('txt_rc').get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), include_hidden_chars=True)
    def plotcommand_set_text(self, text):
        buf = w('txt_rc').get_buffer()
        buf.set_text(text)# }}}

    ## == File tree browser ==
    def on_treeview1_row_expanded(self, treeView, treeIter, treePath):# {{{

        ## Add the children 
        treeStore = treeView.get_model()
        newFilePath = treeStore.get_value(treeIter, 0)      # get the full path of the position
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

        ## Update the plot command
        if w('rad_plotstyle_rc').get_active():
             ## TODO if it does not exist
            self.update_plotcommand_from_rcfile(allow_overwrite_by_empty=False)
        elif self.relevant_rc_filename():
            w('rad_plotstyle_rc').set_active(True)

        ## Update the graphical presentation
        self.plot_reset()               ## first delete the curves, to hide (also) unselected plots
        self.plot_all_sel_records()     ## then show the selected ones
    # }}}
    def treeview1_selectmethod(self, selection, model, treePath, is_selected, user_data):# {{{
        ## TODO reasonable behaviour for block-selection over different unpacked directories/files
        ## Expand a directory by clicking, but do not allow user to select it
        treeIter        = self.tsFiles.get_iter(treePath)
        #self.treeStoreColumns=      {'filepath':0, 'icon':1, 'name':2, 'plotstyleicon':3, 'column':4, 'spreadsheet':5, 'rowtype':6}

        if self.lockTreeViewEvents: return      ## during folding, prevent triggering 'on_select' events on all node children 
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
                #expanded_row_names = self.remember_treeView_expanded_rows(self.tsFiles, w('treeview1'))     TEST
                #selected_row_names = self.remember_treeView_selected_rows(self.tsFiles, w('treeview1'))
                #self.populateTreeStore(self.tsFiles, reset_path=os.path.dirname(self.row_prop(treeIter, 'filepath')))       
                self.populateTreeStore_keep_exp_and_sel(reset_path=os.path.dirname(self.row_prop(treeIter, 'filepath')))
            elif w('treeview1').row_expanded(treePath):
                w('treeview1').collapse_row(treePath)
            elif not w('treeview1').row_expanded(treePath) :
                w('treeview1').expand_row(treePath, open_all=False)
            return False
    # }}}
    def populateTreeStore_keep_exp_and_sel(self, *args, reset_path=None):
        """ Wrapper around populateTreeStore that maintains the selected and expanded rows """
        expanded_row_names = self.remember_treeView_expanded_rows(self.tsFiles, w('treeview1'))    
        selected_row_names = self.remember_treeView_selected_rows(self.tsFiles, w('treeview1'))
        # Passing parent=None will populate the whole tree again
        #self.lockTreeViewEvents = True
        self.populateTreeStore(self.tsFiles, reset_path=reset_path)       
        #self.lockTreeViewEvents = False
        print(expanded_row_names)
        self.restore_treeView_expanded_rows(expanded_row_names)
        self.restore_treeView_selected_rows(selected_row_names)

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
