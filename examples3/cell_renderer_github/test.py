from gi.repository import Gtk, Gdk, GLib
from gi.repository import GdkPixbuf
import cairo

class CellRenderFade(Gtk.CellRenderer):
    def __init__(self, param):
        super(CellRenderFade, self).__init__()
        self.alpha = 0
        self.step = param

    def do_render(self, cr, widget, bg_area, cell_area, flags):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            '/usr/share/pixmaps/blueman/blueman-rssi-70.png',
            cell_area.width, cell_area.height, True)
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, cell_area.x, cell_area.y)

        ## Draw red filled square
        cr.set_source_rgb(1, 0, 0)
        cr.rectangle(cell_area.x, cell_area.y, 10,10)
        cr.fill() 

        ## Draw green outlined square
        cr.set_source_rgb(0, .8, 0)
        cr.rectangle(cell_area.x+5, cell_area.y+5, 10,10)
        cr.stroke() 

        ## Draw blue line
        cr.set_source_rgb(0, 0, .8)
        cr.move_to(cell_area.x+5, cell_area.y+5)
        cr.line_to(cell_area.x+15, cell_area.y+15)
        cr.stroke()

        ## Semitransparent overwrite of whole image
        cr.set_source_rgb(0,0,0)
        cr.paint_with_alpha(self.alpha)


        GLib.timeout_add(15, self.start_fade, widget, cell_area)


    def start_fade(self, widget, cell_area):
        if self.alpha > 1:
            return

        print('Fade', self.alpha)
        widget.queue_draw()
        self.alpha += self.step

class CellRendererFadeWindow(Gtk.Window):

    def __init__(self):
        super(CellRendererFadeWindow, self).__init__(title="CellRendererFade Example")

        self.set_default_size(200, 200)
        self.liststore = Gtk.ListStore(str, str)
        self.liststore.append(["New", Gtk.STOCK_NEW])
        self.liststore.append(["Open", Gtk.STOCK_OPEN])
        self.liststore.append(["Save", Gtk.STOCK_SAVE])

        treeview = Gtk.TreeView(model=self.liststore)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Text", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_pixbuf = CellRenderFade(param=0.001)
        column_pixbuf = Gtk.TreeViewColumn("Image", renderer_pixbuf, stock_id=1)
        treeview.append_column(column_pixbuf)
        self.add(treeview)

win = CellRendererFadeWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
