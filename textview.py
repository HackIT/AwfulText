#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class TextView( gtk.TextView ):
    def __init__(self):
        super( TextView, self ).__init__()
