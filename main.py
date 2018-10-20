#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from awful import AwfulText

if __name__ == "__main__":
    AwfulText()
    gtk.main()