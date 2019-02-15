#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, gobject, pango, pixmap

class CloseButton( gtk.EventBox ):
    def _clicked( self, event, gdkevent, callback=None ):
        if gdkevent.type == gtk.gdk.BUTTON_PRESS:
            self.image.set_from_pixbuf( self.clicked )
        else:
            self.image.set_from_pixbuf( self.normal )
            if callback:
                callback()

    def _notify( self, event, gdkevent ):
        #print self, event, gdkevent, gdkevent.type, self.filemodified
        if gdkevent.type == gtk.gdk.LEAVE_NOTIFY:
            if self.filemodified:
                self.image.set_from_pixbuf( self.modified )
        else:
            self.image.set_from_pixbuf( self.normal )

    def change( self, modified ):
        if type(modified) == bool:
            self.image.set_from_pixbuf( self.modified )
            self.filemodified = modified

    def __init__( self, callback=None ):
        super( CloseButton, self ).__init__()
        self.normal = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.normal_close )
        self.clicked = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.clicked_close )
        self.modified = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.normal_modified )
        self.filemodified = None
        self.image = gtk.Image()
        self.image.set_from_pixbuf( self.normal )
        self.connect( "enter-notify-event", self._notify )
        self.connect( "leave-notify-event", self._notify )
        self.connect( "button-press-event", self._clicked )
        self.connect( "button-release-event", self._clicked, callback ) # shud happen on release ev...
        self.add( self.image )

class ArrowButton( gtk.EventBox ):
    def __clicked( self, event, gdkevent, callback=None ):
        if gdkevent.type == gtk.gdk.BUTTON_PRESS:
            self.image.set_from_pixbuf( self.clicked )
        else:
            self.image.set_from_pixbuf( self.normal )
            if callback:
                callback()

    def __init__( self, normal, clicked=None, callback=None ):
        super( ArrowButton, self ).__init__()
        self.normal = gtk.gdk.pixbuf_new_from_xpm_data( normal )
        if clicked:
            self.clicked = gtk.gdk.pixbuf_new_from_xpm_data( clicked )
        self.image = gtk.Image()
        self.image.set_from_pixbuf( self.normal )
        self.connect( "button-press-event", self.__clicked )
        self.connect( "button-release-event", self.__clicked, callback ) # shud happen on release ev...
        self.add( self.image )

class LabelButton( gtk.EventBox ):
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

class Separator( gtk.EventBox ):
    def __init__( self ):
        super( Separator, self ).__init__()
        self.normal = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.separator )
        self.image = gtk.Image()
        self.image.set_from_pixbuf( self.normal )
        self.add( self.image )

class Notebook( gtk.HBox ):
    _fgcolor = "#aaaaaa"
    def edited( self, *vars ):
        print self, vars
    
    def _filename(self, filename):
        self.filename.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+filename+'</span>')

    def _modified(self, buffer):
        if not self.closeFile.filemodified:
            self.closeFile.change(True)

    def _fileinfo(self, info):
        self.fileinfo.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+info+'</span>')

    def _build(self, build):
        self.build.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+build+'</span>')

    def _openfilemeta(self, meta):
        self.openfilemeta.label.set_markup('<span foreground="'+self._fgcolor+'" weight="bold">'+meta+'</span>')

    def _separator(self):
        return Separator()

    def __init__( self, gtkWindow ):
        super( Notebook, self ).__init__()
        self.root_window = gtkWindow
        self.set_size_request( 0, 20 )
        self.set_spacing(2)
        
        self.filename = LabelButton("Untitled...")
        self.closeFile = CloseButton(callback=gtkWindow.close)
        self.openfilemeta = LabelButton('0:0')
        self.build = LabelButton('build')
        self.language = LabelButton('lang')
        self.tabs = LabelButton('spaces:4')
        self.fileinfo = LabelButton('0:0:0')
        
        self.entry = gtk.Entry()
        self.entry.set_has_frame(False)
        self.entry.connect('key-press-event', self.edited)

        self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        # self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        # line:column:size(byte)
        self.pack_start(self.fileinfo, expand=False, fill=False, padding=2)

        #self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        self.pack_start(self._separator(), expand=False, fill=False, padding=0)

        # filename
        self.pack_start(self.filename, expand=False, fill=False, padding=2)
        # close button
        self.pack_start(self.closeFile, expand=False, fill=False, padding=0)
        #self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        
        # buffer switches
        self.pack_start(ArrowButton(pixmap.normal_left, pixmap.clicked_left), expand=False, fill=False, padding=0)
        self.pack_start(self.openfilemeta, expand=False, fill=False, padding=0)
        self.pack_start(ArrowButton(pixmap.normal_right, pixmap.clicked_right), expand=False, fill=False, padding=0)
        #self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        
        # 
        #self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        #self.pack_start(self.entry)
        #self.pack_start(self._separator(), expand=False, fill=False, padding=0)
        #self.pack_end(self._separator(), expand=False, fill=False, padding=0)
        self.pack_end(self._separator(), expand=False, fill=False, padding=0)

        self.pack_end(self.build, expand=False, fill=False, padding=2)
        #self.pack_end(self._separator(), expand=False, fill=False, padding=0)
        self.pack_end(self._separator(), expand=False, fill=False, padding=0)
        self.pack_end(self.tabs, expand=False, fill=False, padding=2)
        #self.pack_end(self._separator(), expand=False, fill=False, padding=0)
        self.pack_end(self._separator(), expand=False, fill=False, padding=0)
        self.pack_end(self.language, expand=False, fill=False, padding=2)
        #self.pack_end(self._separator(), expand=False, fill=False, padding=0)
        self.pack_end(self._separator(), expand=False, fill=False, padding=0)
