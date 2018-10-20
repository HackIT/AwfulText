#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, config, glib

from menu import Menubar # imply dialog
from status import Statusbar
from sourceview import Buffer, View
from console import * # imply textview
from scrolledwindow import *
from treeview import *
from notebook import *

TEXT_PANE = 0
BROWSER_PANE = 1

class AwfulText( gtk.Window ):

    def mainQuit( self, gtkWindow ):
        self.hide_all()
        gtk.main_quit()

    def updateStatusbar( self, Buffer ):
        count = Buffer.get_char_count()
        iter = Buffer.get_iter_at_mark( Buffer.get_insert() )
        row = iter.get_line()
        col = iter.get_line_offset()
        self.statusbar.push(
            'Line %d; column %d; size %d; ' % (row, col, count) )

    def updateTextmark( self, Buffer, TextIter, TextMark ):
        #self.statusbar.pop(0)
        count = Buffer.get_char_count()
        iter = Buffer.get_iter_at_mark( Buffer.get_insert() )
        row = iter.get_line()
        col = iter.get_line_offset()
        self.statusbar.push(
            'Cursor: line %d, column %d; Filesize: %d' % (row, col, count) )

    def toggleConsole( self, widget ):
        if widget.active:
            self.console.show()
        else:
            self.console.hide()

    def toggleFileBrowser( self, widget ):
        if widget.active:
            self.sw[BROWSER_PANE].show()
        else:
            self.sw[BROWSER_PANE].hide()

    def registerMainScreens( self ):
        # vpanes
        # 1 => hpanes
        # 2 => console
        # hpanes
        # 1 => file browser
        # 2 => notebooks
        self.sw = []
        for i in range(2):
            self.sw.append( ScrolledWindow() )

        self.sw[TEXT_PANE].add( self.view )
        self.sw[BROWSER_PANE].add_with_viewport( self.filebrowser )

        vbox = gtk.VBox()
        vbox.pack_start(Notebook(), False)
        vbox.pack_start(self.sw[TEXT_PANE])


        self.hpanes = gtk.HPaned()
        self.hpanes.pack1( self.sw[BROWSER_PANE], False, False )
        self.hpanes.pack2( vbox, True, True )
        self.hpanes.set_position( 120 )

        self.vpanes = gtk.VPaned()
        self.vpanes.pack1( self.hpanes, False, False )
        self.vpanes.pack2( self.console, False, False )

        container = gtk.VBox()
        container.pack_start( self.menubar, False, False, 0 )
        container.pack_start( self.vpanes, True, True, 0 )
        container.pack_start( self.statusbar, False, False, 0 )
        self.add( container )
        self.show_all()
        self.set_size_request(0,0)

    def __init__(self):
        super( AwfulText, self ).__init__()
        self.set_title( "Untitled - AwfulText" )
        
        self.accelGroup = gtk.AccelGroup()
        self.add_accel_group( self.accelGroup )
        
        try:
            self.set_icon_from_file( config.progIcon )
        except Exception, e:
            print e.message

        self.connect( "destroy", self.mainQuit )
        self.set_size_request( 480, 320 )
        self.set_position( gtk.WIN_POS_CENTER )

        #self.set_border_width(10)
        #self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))

        # TEXTEDITOR
        self.buffer = Buffer()
        self.view = View( self.buffer )
        # happens when buffer changes...
        self.buffer.connect( 'changed', self.updateStatusbar )
        # on cursor mark set
        self.buffer.connect( 'mark_set', self.updateTextmark )

        # STATUSBAR
        # Throwing the object tree through...
        # to handle some window properties/attributes.
        self.statusbar = Statusbar(self)

        # FILEBROWSER
        self.filebrowser = FileBrowser(self)

        # MENUBAR
        # Throwing the object tree through...
        # to handle some window properties/attributes.
        self.menubar = Menubar(self)

        # CONSOLE
        self.console = Console()

        self.registerMainScreens()
        # TODO user config validation

        if not config.window_menu:
            self.menubar.disable()

        if not config.window_statusbar:
            self.statusbar.disable()

        if not config.window_sidepane:
            self.sw[BROWSER_PANE].hide()

        if not config.window_console:
            self.console.hide()
