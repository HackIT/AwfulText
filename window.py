#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk, gtk, gobject, dialog, gtksourceview2

# you must store menu in order to avoid shitty widget flashes!

menu = gtk.Menu()

class app():
	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_title("testapp")
		window.set_default_size(320,240)
		window.connect("destroy", gtk.main_quit)
		window.connect("button-press-event", popup)
		window.connect("button-release-event", rel)
		window.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
		self.view = gtksourceview2.View()
		window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
		#window.add(self.view)
		window.show_all()
		

class buf():
	def __init__(self):
		self.bufStore = []
	def add(self):
		self.bufStore.append(gtksourceview2.Buffer())
	def save(self):
		return
	def select(self):
		return
	def remove(self):
		return

def yo(win, event):
	print win, event

def rel(win, event):
	print win, event

def popup(win, event):
	print win, event, "popup"
	if event.button == 3:
		menuItem = gtk.MenuItem("test")
		menuItem.show()
		menu.append(menuItem)
		menu.connect("client-event", yo )
		menu.popup(None, None, None, event.button, event.get_time())

app()
gtk.main()