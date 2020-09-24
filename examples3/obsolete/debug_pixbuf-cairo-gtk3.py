#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf, Colorspace, PixbufLoader

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
from gi.repository import Gtk, Gdk
filledpixbuf = Pixbuf.new(Colorspace.RGB, True, 8, 16, 16)  ## In fact, it is RGBA
filledpixbuf.fill(0xff9922ff) 
treestore.append(None, [filledpixbuf, "data with a custom color filled image"])


px = PixbufLoader.new_with_type('pnm')
#color = b'\xee\xff\x2d'
#px.write(b'P6\n\n1 1\n255\n' + color)
#px.write(color)
iconpnm = b"""P2 24 7 25
0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
0  3  3  3  3  0  0  7  7  7  7  0  0 11 11 11 11  0  0 15 15 15 15  0
0  3  0  0  0  0  0  7  0  0  0  0  0 11  0  0  0  0  0 15  0  0 15  0
0  3  3  3  0  0  0  7  7  7  0  0  0 11 11 11  0  0  0 15 15 15 15  0
0  3  0  0  0  0  0  7  0  0  0  0  0 11  0  0  0  0  0 15  0  0  0  0
0  3  0  0  0  0  0  7  7  7  7  0  0 11 11 11 11  0  0 15  0  0  0  0
0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
"""
px.write(iconpnm)
px.close()
treestore.append(None, [px.get_pixbuf(), "data with an image loaded from a custom inline PNM file (tedious)"])




## Add a row with a custom-drawn image (cannot do)



from gi.repository import GdkPixbuf
import cairo


class MyCellRenderer(Gtk.CellRenderer):
    def __init__(self, rgb_triplet):
        Gtk.CellRenderer.__init__(self)
        self.rgb_triplet = rgb_triplet
    def do_render(self, cr, widget, bg_area, cell_area, flags):
        pixbuf = GdkPixbuf.Pixbuf.new(Colorspace.RGB, True, 8, cell_area.width, cell_area.height)
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, cell_area.x, cell_area.y)

        ## Draw a filled square
        cr.set_source_rgb(*self.rgb_triplet)
        cr.rectangle(cell_area.x+1, cell_area.y+1, cell_area.width-2, cell_area.height-2)
        cr.fill() 

        ## Outline it black 
        cr.set_source_rgb(0, .8, 0)
        cr.rectangle(cell_area.x+1, cell_area.y+1, cell_area.width-2, cell_area.height-2)
        cr.stroke() 

        ## Draw a blue line
        #cr.set_source_rgb(0, 0, .8)
        #cr.move_to(cell_area.x+5, cell_area.y+5)
        #cr.line_to(cell_area.x+15, cell_area.y+15)
        #cr.stroke()

        ## Semitransparent overwrite of whole image
        #cr.set_source_rgb(0,0,0)
        #cr.paint_with_alpha(self.alpha)


renderer_pixbuf = MyCellRenderer(rgb_triplet=(1.0,.7, .0))
column_pixbuf = Gtk.TreeViewColumn("Image", renderer_pixbuf, stock_id=1)
treeview.append_column(column_pixbuf)

Gtk.main()

