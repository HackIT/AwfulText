#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk

class ScrolledWindow( gtk.ScrolledWindow ):
    def __init__(self):
        super( ScrolledWindow, self ).__init__()
        self.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )

