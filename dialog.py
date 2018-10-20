import pygtk
pygtk.require('2.0')
import gtk, config

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

class SaveFileDialog( gtk.FileChooserDialog ):
    def __init__( self ):
        super( FileSaveDialog, self ).__init__(
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