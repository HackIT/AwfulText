#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, config, glib

from menu import Menubar # imply dialog
from status import Statusbar
from sourceview import Buffer, View
from console import * # imply textview
from scrolledwindow import *
from treeview import *
from notebook import *
from dialog import SaveFileDialog, OpenFileDialog, Message

class AwfulText( gtk.Window ):
    bufstore = []
    bufindex = 1

    def mainQuit( self, gtkWindow ):
        self.close() # save session here
        self.hide_all()
        gtk.main_quit()
        return False

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
        #self.statusbar.push(
        #    'Cursor: line %d, column %d; Filesize: %d' % (row, col, count) )
        self.notebook._fileinfo('%d:%d:%d' % (row, col, count))
    
    def toggleConsole( self, widget ):
        if widget.active:
            self.console.show()
        else:
            self.console.hide()

    def toggleFolderTree( self, widget ):
        if widget.active:
            self.treeview.show()
        else:
            self.treeview.hide()

    def newFile(self, ImageMenuItem):
        self._openFile()
#
    def openFile(self, ImageMenuItem):
        dialog = OpenFileDialog()
        dialog.set_default_response( gtk.RESPONSE_CANCEL )
        
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            dialog.destroy()
            if os.path.isdir(filename):
                return
            self._openFile(filename)
        dialog.destroy()

    def _openFile(self, filename=None):
        self.newBuf()
        if filename:
            self.buffer.showFile(filename)
            #self.filebrowser.listInsert(filename)
            filename = os.path.basename(filename)
        else:
            filename = "Untitled..."
            #self.filebrowser.listInsert(filename)
        self.set_title(filename+' - AwfulText')
        self.notebook._filename(filename)
        self.notebook._openfilemeta('%d:%d' % (self.bufindex,self.bufstore.__len__()) )

    def newBuf(self):
        self.view.set_buffer(Buffer())
        self.buffer = self.view.get_buffer()
        self.bufstore.append( self.buffer )
        self.bufindex += 1
        # happens when buffer changes...
        self.addHandler(self.buffer.connect( 'changed', self.notebook._modified ))
        # on cursor mark set
        self.addHandler(self.buffer.connect( 'mark_set', self.updateTextmark ))

    def closeBuf(self):
        if self.bufstore.__len__() >= 1:
            self.bufstore.pop(self.bufstore.index(self.buffer))
            self.bufindex -= 1
        handlerIds = self.buffer.get_data('handlerIds')
        if handlerIds:
            for n in handlerIds:
                self.buffer.disconnect(n)
        if self.bufstore.__len__() == 0:
            self._openFile() # open up a new buff if there is none remaining...
        else:
            self.buffer = self.bufstore[self.bufstore.__len__()-1]
            self.view.set_buffer(self.buffer)
            print "view buffer change", self.bufstore
        self.notebook.closeFile.change(self.buffer.get_modified())
        self.notebook._openfilemeta( '%d:%d' % ( self.bufindex,self.bufstore.__len__() ) )

    def addHandler(self, handler):
        handlerIds = self.buffer.get_data('handlerIds')
        if not handlerIds:
            handlerIds = []
            handlerIds.append(handler)
        else:
            handlerIds.append(handler)
        self.buffer.set_data('handlerIds', handlerIds)

    def close(self, ImageMenuItem=None):
        if self.buffer.get_modified():
            filename = self.buffer.get_data('fullpath')
            if filename:
                filename = os.path.basename(filename)
            else:
                filename = "Untitled..."
            label = "Save changes to '"+ filename +"'?"
            if Message(self, label): # needs cancel handling...
                if filename == "Untitled...":
                    self.saveAs()
                else:
                    self.save()
        self.closeBuf()

    def addFolder(self, ImageMenuItem=None):
        dialog = OpenFolderDialog()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            dialog.destroy()
            if filename:
                self.filebrowser.renderFolder(filename)
        else:
            dialog.destroy()

    def openFolder(self, ImageMenuItem):
        self.filebrowser.clearTreeStore()
        self.addFolder()

    def saveAs(self, ImageMenuItem=None):
        self.buffer.saveAs()
        filename = self.buffer.get_data('fullpath')
        if filename:
            self.notebook._filename(filename)
            self.set_title(filename+' - AwfulText')

    def save(self, ImageMenuItem=None):
        self.buffer.save()

    def registerContainers( self ):
        self.textview = ScrolledWindow()
        self.textview.add(self.view)
        self.treeview = ScrolledWindow()
        self.treeview.add_with_viewport(self.filebrowser)
        
        editor_container = gtk.VBox()
        editor_container.pack_start(self.notebook, expand=False)
        editor_container.pack_start(self.textview)

        hpaned_container = gtk.HPaned()
        hpaned_container.pack1(self.treeview, shrink=False)
        hpaned_container.pack2(editor_container)
        hpaned_container.set_position(120)

        vpaned_container = gtk.VPaned()
        vpaned_container.pack1(hpaned_container, shrink=False)
        vpaned_container.pack2(self.console)

        glob_container = gtk.VBox()
        glob_container.pack_start( self.menubar, expand=False, fill=False, padding=0)
        glob_container.pack_start( vpaned_container)
        glob_container.pack_start( self.statusbar, expand=False, fill=False, padding=0)

        return glob_container

    def __init__(self):
        super( AwfulText, self ).__init__()
        self.set_title( "Untitled... - AwfulText" )
        
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
        # get record from presentation buffer...
        # that buff is mainly used for file presentation.
        # if buff change it adds a new record
        self.bufstore.append( self.buffer )
        # happens when buffer changes...
        # self.buffer.connect( 'changed', self.updateStatusbar )
        # on cursor mark set
        self.addHandler(self.buffer.connect( 'mark_set', self.updateTextmark ))
        # STATUSBAR
        # Throwing the object tree through...
        # to handle some window properties/attributes.
        self.statusbar = Statusbar(self)

        # FILEBROWSER
        self.filebrowser = FolderTree(self)

        self.notebook = Notebook(self)
        self.notebook._openfilemeta('%d:%d' % (self.bufindex,self.bufstore.__len__()) )
        self.addHandler(self.buffer.connect( 'changed', self.notebook._modified ))

        # MENUBAR
        # Throwing the object tree through...
        # to handle some window properties/attributes.
        self.menubar = Menubar(self)

        # CONSOLE
        self.console = Console()

        self.add( self.registerContainers() )
        self.show_all()
        self.set_size_request(0,0) # avoid flicker when resizing...

        # TODO user config validation
        if not config.window_menu:
            self.menubar.disable()

        if not config.window_statusbar:
            self.statusbar.disable()

        if not config.window_sidepane:
            self.treeview.hide()

        if not config.window_console:
            self.console.hide()

        self.view.grab_focus()