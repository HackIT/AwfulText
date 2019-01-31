#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, gio, glib

class Monitor(gio.File):
    def dbg(self, *vars):
        print vars

    def __init__(self, filepath):
        super( Monitor, self ).__init__(filepath)
        #dirs = gio.File("/tmp")
        mdir = self.monitor_directory()
        mdir.set_rate_limit(0)
        mdir.connect("changed", self.dbg)
        print "done"
