#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf,Colorspace

## Define the structure of the data to be shown in the treeview: one column with an icon and a text (easy)
treestore = Gtk.TreeStore(Pixbuf, str)
treeViewCol = Gtk.TreeViewColumn("FirstColumn")
colCellImg = Gtk.CellRendererPixbuf()
treeViewCol.pack_start(colCellImg, False)
treeViewCol.add_attribute(colCellImg, "pixbuf", 0)
colCellText = Gtk.CellRendererText()
treeViewCol.pack_start(colCellText, True)
treeViewCol.add_attribute(colCellText, "text", 1)

## Build the GUI
treeview = Gtk.TreeView(treestore)
treeview.append_column(treeViewCol)
scrollView = Gtk.ScrolledWindow()
scrollView.add(treeview)
window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.add(scrollView)
window.connect("delete-event", Gtk.main_quit)
window.show_all()
window.set_size_request(500, 500)

## Add a row without own image (easy)
treestore.append(None, [None, "data without own image"])

## Add a row with a stock icon (also easy)
iconpixbuf = Gtk.IconTheme.get_default().load_icon("folder", 16, 0)
treestore.append(None, [iconpixbuf, "data with a stock icon"])

## Add a row with an image from disk (still easy, uncomment if you have a suitable image file)
#loadedpixbuf = Pixbuf.new_from_file_at_size("../../img/logo.png", 125, 125) 
#treestore.append(None, [loadedpixbuf, "data with a custom image from disk"])

## Add a row with a flat-painted image (easy, but not always useful...)
from gi.repository import GLib, Gtk, Gdk, GObject
filledpixbuf = Pixbuf.new(Colorspace.RGB, True, 8, 16, 16)  ## In fact, it is RGBA
filledpixbuf.fill(0xff9922ff) 
treestore.append(None, [filledpixbuf, "data with a custom color filled image"])

## Add a row with a custom-drawn image (cannot do)
import cairo                       # one "cairo" is not ...
#from gi.repository import cairo     # ... the other "cairo" (which does not even contain ImageSurface)
drawnpixbuf = filledpixbuf.copy()
img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 50, 50)
cc = cairo.Context(img)
cc.set_source_rgb(.8, .0, .0) # Cairo uses floats from 0 to 1 for RGB values
cc.rectangle(5,5,5,30)
cc.fill()
cc.set_source_rgb(.5, .9, .2)
cc.move_to(5,5) ## (not visible, but this is a minor problem)
cc.line_to(100,100)
cc.stroke()   ## if I was not interested in Pixbuf, I could easily get the result similar to http://stackoverflow.com/questions/10270795/drawing-in-pygobject-python3#10541984
## Something is missing here to connect the drawing to pixbuf
## This was used by somebody, but does not exist in Gtk3: drawnpixbuf = img.get_pixbuf() 
## This was used by somebody, but does not exist in Gtk3: img.set_source_pixbuf(drawnpixbuf, 0, 0)
## This was used by somebody, but in Gtk3 it reports that the 'get_data' function is not implemented yet: Pixbuf.new_from_data(img.get_data(), cairo.FORMAT_ARGB32, false, 8, 50,50, 50*3)
## None of these methods exists in Gtk3, but I believe there must be some reasonable way to do it.
treestore.append(None, [drawnpixbuf, "data with a custom drawn image, which does not work so far"])

Gtk.main()

