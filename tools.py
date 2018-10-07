import pygtk
pygtk.require('2.0')
import gtk

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

