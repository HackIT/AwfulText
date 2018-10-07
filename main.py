#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, config

from menu import Menubar # imply dialog
from status import Statusbar
from sourceview import Buffer, View
from console import * # imply textview
from scrolledwindow import *
from treeview import *

TEXT_PANE = 0
BROWSER_PANE = 1

class mainWindow( gtk.Window ):
    #def statusbarView(self, widget):
    #    if widget.active: 
    #        self.statusbar.show()
    #    else:
    #        self.statusbar.hide()

    def mainQuit( self, gtkWindow ):
        self.hide_all()
        gtk.main_quit()

    #def dbg(self, arg1=None, arg2=None, arg3=None, arg4=None):
    #    print "self : ", self, "\narg1 : ", arg1, "\narg2 : ", arg2, "\narg3 : ", arg3, "\narg4 : ", arg4, "\n"
    #
    #    if arg2.window:
    #        if arg2.window == arg1.get_window(gtk.TEXT_WINDOW_LEFT):
    #            arg2.window.set_cursor( gtk.gdk.Cursor( gtk.gdk.LEFT_PTR ) )
    #        else:
    #            arg2.window.set_cursor( gtk.gdk.Cursor( gtk.gdk.XTERM ) )

    def update_statusbar( self, Buffer ):
        count = Buffer.get_char_count()
        iter = Buffer.get_iter_at_mark( Buffer.get_insert() )
        row = iter.get_line()
        col = iter.get_line_offset()
        self.statusbar.push(
            'Line %d; column %d; size %d; ' % (row, col, count) )

    def update_textmark( self, Buffer, TextIter, TextMark ):
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

    def register_main_screens( self ):
        # vpanes
        # 1 => hpanes
        # 2 => console
        # hpanes
        # 1 => file browser
        # 2 => notebooks


        self.sw = []
        for i in range(2):
            self.sw.append( ScrolledWindow() )

        #for i in range(2):
        #    self.sw[i].set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )

        self.sw[TEXT_PANE].add( self.view )
        self.sw[BROWSER_PANE].add_with_viewport( self.filebrowser )

        self.hpanes = gtk.HPaned()
        self.hpanes.pack1( self.sw[BROWSER_PANE], False, False )
        self.hpanes.pack2( self.sw[TEXT_PANE], False, False )
        self.hpanes.set_position( 200 )

        self.vpanes = gtk.VPaned()
        self.vpanes.pack1( self.hpanes, False, False )
        self.vpanes.pack2( self.console, False, False )
        self.vpanes.set_position( 350 )

        container = gtk.VBox()
        container.pack_start( self.menubar, False, False, 0 )
        container.pack_start( self.vpanes, True, True, 0 )
        container.pack_start( self.statusbar, False, False, 0 )
        self.add( container )
        self.show_all()

    def __init__(self):
        super( mainWindow, self ).__init__()
        self.set_title( "AwfulText" )

        try:
            self.set_icon_from_file( config.progIcon )
        except Exception, e:
            print e.message

        self.connect( "destroy", self.mainQuit )
        #self.set_size_request( 640, 480 )
        self.set_position( gtk.WIN_POS_CENTER )

        #self.set_border_width(10)
        #self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))

        # TEXTEDITOR
        self.buffer = Buffer()
        self.view = View( self.buffer )
        # happens when buffer changes...
        self.buffer.connect( 'changed', self.update_statusbar )
        # on cursor mark set
        self.buffer.connect( 'mark_set', self.update_textmark )

        # STATUSBAR
        # Throwing the object tree through...
        # to handle some window properties/attributes.
        self.statusbar = Statusbar( self )

        # FILEBROWSER
        self.filebrowser = FileBrowser()

        # MENUBAR
        # Throwing the object tree through...
        # to handle some window properties/attributes.
        self.menubar = Menubar( self )

        # CONSOLE
        self.console = Console()

        self.register_main_screens()
        # TODO user config validation

        if not config.window_menu:
            self.menubar.disable()

        if not config.window_statusbar:
            self.statusbar.disable()

        if not config.window_sidepane:
            self.sw[BROWSER_PANE].hide()

        if not config.window_console:
            self.console.hide()

if __name__ == "__main__":
    mainWindow()
    gtk.main()
