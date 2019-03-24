            #for i in gtk.gdk.pixbuf_get_formats():
            #    for n in i['extensions']:
            #        if re.search(n+'$', filename):
            #            gdkImage = gtk.gdk.pixbuf_new_from_file(filename)
            #            gtkImage = gtk.Image()
            #            gtkImage.set_from_pixbuf(gdkImage)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk, gtk, gobject, dialog, re

# you must store menu in order to avoid artifacts!

menu = gtk.Menu()

class app():
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("testapp")
        window.set_default_size(320,240)
        window.connect("destroy", gtk.main_quit)
        window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
        filename = "/home/dirtybit/AwfulText/icon.png"
        gdkImage = gtk.gdk.pixbuf_new_from_file(filename)
        gtkImage = gtk.Image()
        gtkImage.set_from_pixbuf(gdkImage)
        window.add(gtkImage)
        window.show_all()

def yo(win, event):
    print win, event

def rel(win, event):
    print win, event

def popup(win, event):
    print win, event
    if event.button == 3:
        menuItem = gtk.MenuItem("test")
        menuItem.show()
        menu.append(menuItem)
        menu.connect("client-event", yo )
        menu.popup(None, None, None, event.button, event.get_time())

app()
gtk.main()