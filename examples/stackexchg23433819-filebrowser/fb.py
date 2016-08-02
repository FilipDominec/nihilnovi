#!/usr/bin/python
import os, stat
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

def populateFileSystemTreeStore(treeStore, path, parent=None):
    itemCounter = 0
    # iterate over the items in the path
    for item in os.listdir(path):
        # Get the absolute path of the item
        itemFullname = os.path.join(path, item)
        # Extract metadata from the item
        itemMetaData = os.stat(itemFullname)
        # Determine if the item is a folder
        itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
        # Generate an icon from the default icon theme
        itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "empty", 8, 0)
        # Append the item to the TreeStore
        currentIter = treeStore.append(parent, [item, itemIcon, itemFullname])
        # add dummy if current item was a folder
        if itemIsFolder: treeStore.append(currentIter, [None, None, None])
        #increment the item counter
        itemCounter += 1
    # add the dummy node back if nothing was inserted before
    if itemCounter < 1: treeStore.append(parent, [None, None, None])

def onRowExpanded(treeView, treeIter, treePath):
    # get the associated model
    treeStore = treeView.get_model()
    # get the full path of the position
    newPath = treeStore.get_value(treeIter, 2)
    # populate the subtree on curent position
    populateFileSystemTreeStore(treeStore, newPath, treeIter)
    # remove the first child (dummy node)
    treeStore.remove(treeStore.iter_children(treeIter))

def onRowCollapsed(treeView, treeIter, treePath):
    # get the associated model
    treeStore = treeView.get_model()
    # get the iterator of the first child
    currentChildIter = treeStore.iter_children(treeIter)
    # loop as long as some childern exist
    while currentChildIter:
        # remove the first child
        treeStore.remove(currentChildIter)
        # refresh the iterator of the next child
        currentChildIter = treeStore.iter_children(treeIter)
    # append dummy node
    treeStore.append(treeIter, [None, None, None])

window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)

# initialize the filesystem treestore
fileSystemTreeStore = Gtk.TreeStore(str, Pixbuf, str)
# populate the tree store
populateFileSystemTreeStore(fileSystemTreeStore, '/home')
# initialize the TreeView
fileSystemTreeView = Gtk.TreeView(fileSystemTreeStore)

# Create a TreeViewColumn
treeViewCol = Gtk.TreeViewColumn("File")
# Create a column cell to display text
colCellText = Gtk.CellRendererText()
# Create a column cell to display an image
colCellImg = Gtk.CellRendererPixbuf()
# Add the cells to the column
treeViewCol.pack_start(colCellImg, False)
treeViewCol.pack_start(colCellText, True)
# Bind the text cell to column 0 of the tree's model
treeViewCol.add_attribute(colCellText, "text", 0)
# Bind the image cell to column 1 of the tree's model
treeViewCol.add_attribute(colCellImg, "pixbuf", 1)
# Append the columns to the TreeView
fileSystemTreeView.append_column(treeViewCol)
# add "on expand" callback
fileSystemTreeView.connect("row-expanded", onRowExpanded)
# add "on collapse" callback
fileSystemTreeView.connect("row-collapsed", onRowCollapsed)
scrollView = Gtk.ScrolledWindow()
scrollView.add(fileSystemTreeView)

# append the scrollView to the window (this)
window.add(scrollView)

window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
