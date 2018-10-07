#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from scrolledwindow import *
from textview import *

class Console( ScrolledWindow ):
    def __init__( self ):
        super( Console, self ).__init__()
        self.console = TextView()
        self.add( self.console )
        self.mode( False )

    def mode(self, mode):
        if mode: # True = INTERPRETER
            self.console.set_editable(True)
            self.console.set_cursor_visible(True)
        else: # False = DEBUG
            self.console.set_editable(False)
            self.console.set_cursor_visible(False)


