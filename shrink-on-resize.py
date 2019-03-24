#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk, gtk, gobject, dialog
from notebook import *
# you must store menu in order to avoid shitty widget flashes!

menu = gtk.Menu()

class app(gtk.Window):
    def dbg(self, *vars):
        print vars, self.get_size()

    def __init__(self):
        super( app, self ).__init__()
        self.set_title("testapp")
        self.set_default_size(320,0)
        self.connect("check-resize", self.dbg)
        self.connect("destroy", gtk.main_quit)
        self.notebook = Notebook(self)
        self.add(self.notebook)
        self.show_all()

    def close():
        pass

app()
gtk.main()