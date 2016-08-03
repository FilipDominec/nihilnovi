import os, stat         #!/usr/bin/python
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

def populateFileSystemTreeStore(treeStore, path, parent=None):
    itemCounter = 0
    for item in os.listdir(path):       # iterate over the items in the path
        itemFullname = os.path.join(path, item)         # Get the absolute path of the item
        itemMetaData = os.stat(itemFullname)        # Extract metadata from the item
        itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)       # Determine if the item is a folder
        itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "empty", 8, 0) # Generate a default icon
        currentIter = treeStore.append(parent, [item, itemIcon, itemFullname])      # Append the item to the TreeStore
        if itemIsFolder: treeStore.append(currentIter, [None, None, None])      # add dummy if current item was a folder
        itemCounter += 1        #increment the item counter
    if itemCounter < 1: treeStore.append(parent, [None, None, None])        # add the dummy node back if nothing was inserted before

def onRowExpanded(treeView, treeIter, treePath):
    treeStore = treeView.get_model()        # get the associated model
    newPath = treeStore.get_value(treeIter, 2)      # get the full path of the position
    populateFileSystemTreeStore(treeStore, newPath, treeIter)       # populate the subtree on curent position
    treeStore.remove(treeStore.iter_children(treeIter))         # remove the first child (dummy node)

def onRowCollapsed(treeView, treeIter, treePath):
    treeStore = treeView.get_model()        # get the associated model
    currentChildIter = treeStore.iter_children(treeIter)        # get the iterator of the first child
    while currentChildIter:         # loop as long as some childern exist
        treeStore.remove(currentChildIter)      # remove the first child
        currentChildIter = treeStore.iter_children(treeIter)        # refresh the iterator of the next child
    treeStore.append(treeIter, [None, None, None])      # append dummy node

window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)

fileSystemTreeStore = Gtk.TreeStore(str, Pixbuf, str)       # initialize the filesystem treestore
populateFileSystemTreeStore(fileSystemTreeStore, '/home')       # populate the tree store
fileSystemTreeView = Gtk.TreeView(fileSystemTreeStore)      # initialize the TreeView

treeViewCol = Gtk.TreeViewColumn("File")        # Create a TreeViewColumn
colCellText = Gtk.CellRendererText()        # Create a column cell to display text
colCellImg = Gtk.CellRendererPixbuf()       # Create a column cell to display an image
treeViewCol.pack_start(colCellImg, False)       # Add the cells to the column
treeViewCol.pack_start(colCellText, True)
treeViewCol.add_attribute(colCellText, "text", 0)       # Bind the text cell to column 0 of the tree's model
treeViewCol.add_attribute(colCellImg, "pixbuf", 1)      # Bind the image cell to column 1 of the tree's model
fileSystemTreeView.append_column(treeViewCol)       # Append the columns to the TreeView
fileSystemTreeView.connect("row-expanded", onRowExpanded)       # add "on expand" callback
fileSystemTreeView.connect("row-collapsed", onRowCollapsed)         # add "on collapse" callback
scrollView = Gtk.ScrolledWindow()
scrollView.add(fileSystemTreeView)

window.add(scrollView)      # append the scrollView to the window (this)

window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
