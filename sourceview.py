#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, pango, gtksourceview2, os, sys, string
import config
from dialog import SaveFileDialog, OpenFileDialog

def dbg(*vars):
    for var in vars:
        print var
        #if var.window:
        #    if var.window == var.get_window(gtk.TEXT_WINDOW_LEFT):
        #        var.window.set_cursor( gtk.gdk.Cursor( gtk.gdk.LEFT_PTR ) )
        #    else:
        #        var.window.set_cursor( gtk.gdk.Cursor( gtk.gdk.XTERM ) )

def debug(str):
    if config.__DEBUG__:
        sys.stderr.write(str+"\n")

class StyleSchemeManager( gtksourceview2.StyleSchemeManager ):
    def __init__(self):
        super( StyleSchemeManager, self ).__init__()

class LanguageManager( gtksourceview2.LanguageManager ):
    def __init__(self):
        super( LanguageManager, self ).__init__()
        languages = [ ( string.capitalize ( i ), i ) \
          for i in self.get_language_ids () ]

        languages.sort ()
        self.languages = [ ( 'Default', None ) ] + languages

class Buffer( gtksourceview2.Buffer ):
    def tabsToSpaces(self, menuItem, tabWidth):
        fmt = "%."+str(tabWidth)+"s"
        tab = fmt % "        "
        text = self.get_text(self.get_start_iter(), self.get_end_iter())
        self.set_text(text.replace("\t", tab))

    def spacesToTabs(self, menuItem, tabWidth):
        fmt = "%."+str(tabWidth)+"s"
        tab = fmt % "        "
        text = self.get_text(self.get_start_iter(), self.get_end_iter())
        self.set_text(text.replace(tab, "\t"))

    def update_cursor_position(self, view):
        #tabwidth = view.get_tab_width()
        #pos_label = view.get_data('pos_label')
        #print buffer, view
        iter = self.get_iter_at_mark(self.get_insert())
        nchars = iter.get_offset()
        row = iter.get_line() + 1
        start = iter.copy()
        start.set_line_offset(0)
        col = 0

        while start.compare(iter) < 0:
            if start.get_char() == ' ':
                col += 8 - col % 8
                #print "herrr"
            else:
                col += 1
            start.forward_char()

        debug( 'Line: %d, Column: %d, Chars: %d' % ( row, col, nchars ) )

        #self.feedback = gtk.Label( 'Line: %d, Column: %d, Chars: %d' % (row, col, nchars) )
        #self.statusbar.push(1, 'Line: %d, Column: %d, Chars: %d' % (row, col, nchars))
        #pos_label.set_text('char: %d, line: %d, column: %d' % (nchars, row, col+1))

    def newFile(self):
        self.set_text( "" )
        self.set_modified( False )
        self.place_cursor( self.get_start_iter() )
#
    def showFile( self, filename ):
        if filename:
            #if os.path.isdir(filename):
            #    self.set_text("")
            #    self.set_modified( False )
            #    self.place_cursor( self.get_start_iter() )
            #    self.set_data('fullpath', filename)
            #    return
            #for i in gtk.gdk.pixbuf_get_formats():
            #    for n in i['extensions']:
            #        if re.search(n+'$', filename):
            #            gdkImage = gtk.gdk.pixbuf_new_from_file(filename)
            #            gtkImage = gtk.Image()
            #            gtkImage.set_from_pixbuf(gdkImage)
            #            
            # self.language_manager
            if os.path.isabs(filename):
                path = filename
            #else:
            #    path = os.path.abspath(filename)
            language = self.language_manager.guess_language(filename)
            self.begin_not_undoable_action()
            try:
                txt = open(path, "r")
                data = txt.read()
                txt.close()
            except:
                return False
            
            if language:
                self.set_highlight_syntax(True)
                self.set_language(language)
            else:
                debug( 'No language found for file "%s"' % filename )
                self.set_highlight_syntax(False)

            self.set_text(data)
            self.end_not_undoable_action()
            self.set_modified(False)
            self.set_data('fullpath', path)
            self.place_cursor(self.get_start_iter())

    def saveAs(self):
        dialog = SaveFileDialog()
        dialog.set_default_response( gtk.RESPONSE_OK )
        
        #filter = gtk.FileFilter()
        #filter.set_name("Text Files")
        #filter.add_mime_type("text/data")
        #filter.add_pattern("*.txt")
        #dialog.add_filter(filter)

        #filter = gtk.FileFilter()
        #filter.set_name("All Files")
        #filter.add_pattern("*.*")
        #dialog.add_filter(filter)
        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            self.filename = dialog.get_filename()
            dialog.destroy()
            text = self.get_text(self.get_start_iter() , self.get_end_iter())
            file = open(self.filename, "w")
            file.write(text)
            file.close()
            self.set_modified(False)
            debug("Saved file: " + self.filename)
            # feed visual notebook filename's widget?
        dialog.destroy()

    def save(self):
        self.filename = self.get_data('fullpath')
        if not self.filename:
            return self.saveAs()
        text = self.get_text(self.get_start_iter() , self.get_end_iter())
        file = open(self.filename, "w")
        file.write(text)
        file.close()
        self.set_modified(False)
        debug("Saved file: " + self.filename)

    def __init__( self ):
        super( Buffer, self ).__init__()
        self.set_highlight_syntax( config.highlight_syntax )
        self.set_highlight_matching_brackets( config.highlight_matching_brackets )

        scheme = StyleSchemeManager()
        #style = scheme.get_scheme( config.scheme )
        self.set_style_scheme( scheme.get_scheme( config.scheme ) )
        self.language_manager = LanguageManager()

class View( gtksourceview2.View ):
    def toggleDrawInvisibleCharacters(self, menuItem):
        flags = self.get_draw_spaces()
        print menuItem.active
        if menuItem.active:
            self.set_draw_spaces( gtksourceview2.DRAW_SPACES_SPACE|gtksourceview2.DRAW_SPACES_TAB )
        else:
            self.set_draw_spaces( 0 )
        
        #flags >>= gtksourceview2.DRAW_SPACES_SPACE
        #print bin(flags)
        #print bin(gtksourceview2.DRAW_SPACES_TAB)
        #print bin(gtksourceview2.DRAW_SPACES_SPACE)
        #print bin(gtksourceview2.DRAW_SPACES_ALL)
        #if flags == 0b0:
        #    print 'f', flags, 'a', menuItem
        #    return
        #if (flags << gtksourceview2.DRAW_SPACES_TAB or flags >> gtksourceview2.DRAW_SPACES_TAB): #|gtksourceview2.DRAW_SPACES_TAB:
        #    print flags, menuItem
        #    #self.gtkSourceView.unset_flags(gtksourceview2.DRAW_SPACES_SPACE)
        #    #print self.gtkSourceView.get_draw_spaces()

    def toggleSetSpacesInsteadOfTabs(self, menuItem): 
        if menuItem.active:
            self.set_insert_spaces_instead_of_tabs( True )
        else:
            self.set_insert_spaces_instead_of_tabs( False )

    def toggleLineNumbers(self, menuItem):
        if menuItem.active:
            self.set_show_line_numbers( True )
        else:
            self.set_show_line_numbers( False )

    def toggleHighlightCurrentLine(self, menuItem):
        if menuItem.active:
            self.set_highlight_current_line( True )
        else:
            self.set_highlight_current_line( False )

    def toggleIndentOnTab(self, menuItem):
        if menuItem.active:
            self.set_indent_on_tab( True )
        else:
            self.set_indent_on_tab( False )

    def toggleAutoIndent(self, menuItem):
        if menuItem.active:
            self.set_auto_indent( True )
        else:
            self.set_auto_indent( False )

    def indentWithSpaces(self, menuItem):
        if menuItem.active:
            self.set_insert_spaces_instead_of_tabs( True )
        else:
            self.set_insert_spaces_instead_of_tabs( False )

    def incrIndentWidth(self, menuItem, gtkWindow):
        tabWidth = gtkWindow.tabWidth
        self.tabw += 1
        self.setIndentWidth(tabWidth)

    def setIndentWidth(self, tabWidth):
        self.set_indent_width(self.tabw)
        tabWidth.set_label("Tab: "+str(self.tabw))

    def decrIndentWidth(self, menuItem, gtkWindow):
        tabWidth = gtkWindow.tabWidth
        self.tabw -= 1
        self.setIndentWidth(tabWidth)

    def bufferSwitch(self, switch):
        return

    def __init__( self, Buffer ):
        super( View, self ).__init__()
        self.tabw = config.tab_width
        self.set_indent_width( self.tabw )
        self.set_buffer( Buffer )
        self.set_left_margin( 5 )
        self.set_right_margin( 5 )
        self.set_highlight_current_line( config.highlight_current_line )
        self.set_show_line_numbers( config.show_line_numbers )
        self.set_indent_on_tab( config.indent_on_tab )
        self.set_auto_indent( config.auto_indent )
        self.set_right_margin_position( config.right_margin_position )
        self.set_show_right_margin( config.show_right_margin )
        self.set_insert_spaces_instead_of_tabs( config.insert_spaces_instead_of_tabs )
        if config.draw_spaces == 0:
            self.set_draw_spaces( 0 )
        elif config.draw_spaces == 1:
            self.set_draw_spaces( gtksourceview2.DRAW_SPACES_SPACE )
        else:
            self.set_draw_spaces( gtksourceview2.DRAW_SPACES_SPACE|gtksourceview2.DRAW_SPACES_TAB )
        #self.set_draw_spaces( gtksourceview2.DRAW_SPACES_SPACE|gtksourceview2.DRAW_SPACES_TAB )
        # self.View.set_show_line_marks(True)
        #Buffer.connect( 'changed', Buffer.update_cursor_position, self )
        # self.View.set_mark_category_background("lal", gtk.gdk.color_parse("#ff0000"))
        # self.fontdesc = pango.FontDescription( config.font )
        self.modify_font( pango.FontDescription( config.font ) )

        #self.connect( "motion-notify-event", dbg )
        self.connect( "button-press-event", dbg )
        self.gtkSourceGutter = self.get_gutter( gtk.TEXT_WINDOW_LEFT )

        #self.gtkSourceGutterView = self.gtkSourceGutter.get_property("view")
        #gtkSourceGutterView.connect( "motion-notify-event", self.dbg )

        # A button has been clicked.
        self.gtkSourceGutter.connect( "cell-activated", dbg )
