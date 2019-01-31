#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, gobject, pango

# shud play with opacity instead this...
normal_left = [
    "11 13 2 1",
    ". c #777776",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@.@@@",
    "@@@@@@...@@",
    "@@@@@....@@",
    "@@@@....@@@",
    "@@@@....@@@",
    "@@@@@....@@",
    "@@@@@@...@@",
    "@@@@@@@.@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

clicked_left = [
    "11 13 2 1",
    ". c #aaaaaa",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@.@@@",
    "@@@@@@...@@",
    "@@@@@....@@",
    "@@@@....@@@",
    "@@@@....@@@",
    "@@@@@....@@",
    "@@@@@@...@@",
    "@@@@@@@.@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

normal_right = [
    "11 13 2 1",
    ". c #777776",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@.@@@@@@@",
    "@@...@@@@@@",
    "@@....@@@@@",
    "@@@....@@@@",
    "@@@....@@@@",
    "@@....@@@@@",
    "@@...@@@@@@",
    "@@@.@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

clicked_right = [
    "11 13 2 1",
    ". c #aaaaaa",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@.@@@@@@@",
    "@@...@@@@@@",
    "@@....@@@@@",
    "@@@....@@@@",
    "@@@....@@@@",
    "@@....@@@@@",
    "@@...@@@@@@",
    "@@@.@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

normal_delete = [
    "11 13 3 1",
    ", c #ffffff",
    ". c #777776",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@.@@@.@@@",
    "@@...@...@@",
    "@@.......@@",
    "@@@.....@@@",
    "@@@.....@@@",
    "@@.......@@",
    "@@...@...@@",
    "@@@.@@@.@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

clicked_delete = [
    "11 13 3 1",
    ", c #ffffff",
    ". c #aaaaaa",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@.@@@.@@@",
    "@@...@...@@",
    "@@.......@@",
    "@@@.....@@@",
    "@@@.....@@@",
    "@@.......@@",
    "@@...@...@@",
    "@@@.@@@.@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

class PixbufButton(gtk.EventBox):
    def __clicked(self, event, gdkevent):
        if gdkevent.type == gtk.gdk.BUTTON_PRESS:
            self.image.set_from_pixbuf(self.clicked)
        else:
            self.image.set_from_pixbuf(self.normal)
    
    def __init__( self, normal, clicked ):
        super( PixbufButton, self ).__init__()
        self.normal = gtk.gdk.pixbuf_new_from_xpm_data( normal )
        self.clicked = gtk.gdk.pixbuf_new_from_xpm_data( clicked )
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.normal)
        self.connect("button-press-event", self.__clicked)
        self.connect("button-release-event", self.__clicked)
        self.add(self.image)

class LabelButton(gtk.EventBox):
    def fileMenu(self, label, event):
        print self
        print label
        print event

        #if event.button == 3: # right clik
        #        self.contextMenu( [{'name':'close', 'activate':self.closeSelection, 'path':path, 'event':event }] )
            #selectedIter = self.listStore.get_iter(path)
            #print path, self.listStore.get_value(selectedIter, 1), event

    def contextMenu(self, menuItems):
        # this way cuz catching menu state to remove menu items... may change...
        for i in [None, Menu()]: # pretty strange to me but it's okay for now
            self.menu = i # to have dynamic parameter...
        for m in menuItems:
            menuItem = MenuItem(m['name'])
            menuItem.connect('activate', m['activate'], m['path'])
            self.menu.add(menuItem)
        self.menu.popup(None, None, None, m['event'].button, m['event'].time)

    def __clicked(self, event, gdkevent):
        print self, event, gdkevent

    def __init__(self, str):
        super( LabelButton, self ).__init__()
        self.label = gtk.Label()
        self.label.set_markup('<span foreground="#aaaaaa" weight="bold">'+str+'</span>')
        self.connect("button-press-event", self.__clicked)
        self.connect("button-release-event", self.__clicked)
        self.add(self.label)

class Notebook( gtk.HBox ):
    _fgcolor = "#aaaaaa"
    def edited(self, *vars):
        print self, vars
    
    def _filename(self, filename):
        self.filename.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+filename+'</span>')

    def _fileinfo(self, info):
        self.fileinfo.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+info+'</span>')

    def _build(self, build):
        self.build.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+build+'</span>')

    def _openfilemeta(self, meta):
        self.openfilemeta.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+meta+'</span>')

    def _separator(self):
        separator = gtk.Label()
        separator.set_markup('<span foreground="#777776" weight="bold"> | </span>')
        self.pack_start(separator, expand=False, fill=False, padding=0)

    def __init__( self, gtkWindow ):
        super( Notebook, self ).__init__()
        self.root_window = gtkWindow
        self.set_size_request( 0, 20 )
        self.set_spacing(2)
        
        self.filename = LabelButton('Untitled...')
        self.openfilemeta = LabelButton('0:0')
        self.build = LabelButton('build')
        self.language = LabelButton('lang')
        self.tabs = LabelButton('spaces:4')
        self.fileinfo = LabelButton('0:0:0')
        
        self.entry = gtk.Entry()
        self.entry.set_has_frame(False)
        self.entry.connect('key-press-event', self.edited)

        self._separator()
        self.pack_start(self.fileinfo, expand=False, fill=False, padding=2)
        self._separator()
        self.pack_start(self.filename, expand=False, fill=False, padding=2)
        self.pack_start(PixbufButton(normal_delete, clicked_delete), expand=False, fill=False, padding=0)
        self._separator()
        self.pack_start(PixbufButton(normal_left, clicked_left), expand=False, fill=False, padding=0)
        self.pack_start(self.openfilemeta, expand=False, fill=False, padding=0)
        self.pack_start(PixbufButton(normal_right, clicked_right), expand=False, fill=False, padding=0)
        self._separator()
        self.pack_start(self.entry)
        self._separator()
        self.pack_start(self.build, expand=False, fill=False, padding=2)
        self._separator()
        self.pack_start(self.tabs, expand=False, fill=False, padding=2)
        self._separator()
        self.pack_start(self.language, expand=False, fill=False, padding=2)
        self._separator()


