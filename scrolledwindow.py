#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class ScrolledWindow( gtk.ScrolledWindow ):
    def __init__(self):
        super( ScrolledWindow, self ).__init__()
        self.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
