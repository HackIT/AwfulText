#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, config

def Message(window, label):
    d = gtk.MessageDialog(window, 
        gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION, 
        gtk.BUTTONS_NONE, 
        label)
    d.set_default_size(300, 150)
    d.set_resizable(False)
    d.add_buttons(gtk.STOCK_CANCEL, 0, gtk.STOCK_NO, 1, gtk.STOCK_YES, 2)
    answer = d.run()
    d.destroy()
    if answer == 2:
        return True

class ErrorMessage(gtk.MessageDialog):
    def __init__(self, string):
        super( ErrorMessage, self ).__init__()
        self.set_markup(string)
        self.run()

class About( gtk.AboutDialog ):
    def __init__( self, menuItem ):
        super( About, self ).__init__()
        self.set_size_request(300, 200)
        #print self, menuItem
        #self.set_transient_for(self)
        #self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_program_name(config.progName+"\302\251")
        self.set_version(config.progVer)
        self.set_copyright(config.progCop)
        self.set_comments(config.progCom)
        self.set_website(config.progUrl)
        self.set_logo(gtk.gdk.pixbuf_new_from_file(config.progIcon))
        self.run()
        self.destroy()

class NewFileEntry( gtk.Dialog ):
    def __init__(self):
        super(NewFileEntry, self).__init__()
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.entry = gtk.Entry()
        vbox = self.get_content_area()
        self.entry.set_max_length(50)
        vbox.add(self.entry)
        self.show_all()
        self.run()

#        self.select_region(0, len(self.get_text()))
#        self.connect("activate", self.enter_callback)
#        self.set_text("hello")
#        self.insert_text(" world", len(self.get_text()))
#        self.show()
#    
#    def enter_callback(self, widget, entry):
#        print "Entry contents: %s\n" % self.get_text()
#
#    def dialog_response_callback(self, dialog, response_id):
#        if (response_id != RESPONSE_FORWARD and
#            response_id != RESPONSE_BACKWARD):
#            dialog.destroy()
#            return
#  
#        start, end = dialog.buffer.get_bounds()
#        search_string = start.get_text(end)
#
#        print "Searching for `%s'\n" % search_string
#
#        buffer = self.text_view.get_buffer()
#        if response_id == RESPONSE_FORWARD:
#            buffer.search_forward(search_string, self)
#        elif response_id == RESPONSE_BACKWARD:
#            buffer.search_backward(search_string, self)
#    
#        dialog.destroy()
#
#    def do_search(self, callback_action, widget):
#        search_text = gtk.TextView()
#        dialog = gtk.Dialog("Search", self,
#                            gtk.DIALOG_DESTROY_WITH_PARENT,
#                            ("Forward", RESPONSE_FORWARD,
#                             "Backward", RESPONSE_BACKWARD,
#                             gtk.STOCK_CANCEL, gtk.RESPONSE_NONE))
#        dialog.vbox.pack_end(search_text, True, True, 0)
#        dialog.buffer = search_text.get_buffer()
#        dialog.connect("response", self.dialog_response_callback)
#
#        search_text.show()
#        search_text.grab_focus()
#        dialog.show_all()

class SaveFileDialog( gtk.FileChooserDialog ):
    def __init__( self ):
        super( SaveFileDialog, self ).__init__(
            "Save file...",
            None,
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_SAVE, gtk.RESPONSE_OK)
        )

class OpenFileDialog( gtk.FileChooserDialog ):
    def __init__(self):
        super( OpenFileDialog, self ).__init__(
            'Open file...', None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )

class OpenFolderDialog( gtk.FileChooserDialog ):
    def __init__(self):
        super( OpenFolderDialog, self ).__init__(
            'Open folder...', None,
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )

class ColorDial( gtk.ColorSelectionDialog ):
    def __init__( self, arg ):
        super( ColorDial, self ).__init__("Select color")
        self.set_position(gtk.WIN_POS_CENTER)
        response = self.run()
        if response == gtk.RESPONSE_OK:
            colorsel = self.colorsel
            m = colorsel.get_current_color()
            print m.red, m.green, m.blue, colorsel.get_current_color().to_string(), self.get_color_selection()
        # print response
        #if response == gtk.RESPONSE_OK:
        #    colorsel = colordial.colorsel
        #    color = colorsel.get_current_color()
        #    self.label.modify_fg(gtk.STATE_NORMAL, color)
        self.destroy()