import pygtk
pygtk.require('2.0')
import gtk, config

class Statusbar( gtk.HBox ):
    def __init__( self, gtkWindow ):
        super( Statusbar, self ).__init__()
        menub = gtk.MenuBar()
        menub.set_pack_direction( gtk.PACK_DIRECTION_RTL )
        menuSpaces = gtk.MenuItem( "Spaces: "+str( gtkWindow.view.tabw ) )
        subMenuSpaces = gtk.Menu()
        menuSpaces.set_submenu( subMenuSpaces )

        drawSpaces = gtk.CheckMenuItem( "Show spaces & tabs" )
        drawSpaces.set_active( True )
        drawSpaces.connect( "activate", gtkWindow.view.toggleDrawInvisibleCharacters )

        indentOnTab = gtk.CheckMenuItem( "Indent on tab" )
        indentOnTab.set_active( config.indent_on_tab )
        indentOnTab.connect( "activate", gtkWindow.view.toggleIndentOnTab )

        autoIndent = gtk.CheckMenuItem( "Auto indent" )
        autoIndent.set_active( config.auto_indent )
        autoIndent.connect( "activate", gtkWindow.view.toggleAutoIndent )

        indentSpaces = gtk.CheckMenuItem( "Use spaces instead of tabs" )
        indentSpaces.connect( "activate", gtkWindow.view.indentWithSpaces )

        incrTabWidth = gtk.MenuItem( "Increase" )
        incrTabWidth.connect( "activate", gtkWindow.view.incrIndentWidth )

        gtkWindow.tabWidth = gtk.MenuItem( "Tab: "+str( gtkWindow.view.tabw ) )
        #tabWidth.connect("activate", self.)

        decrTabWidth = gtk.MenuItem( "Decrease" )
        decrTabWidth.connect( "activate", gtkWindow.view.decrIndentWidth )

        tabsToSpaces = gtk.MenuItem( "Convert tabs to spaces" )
        tabsToSpaces.connect( "activate", exit )

        spacesToTabs = gtk.MenuItem( "Convert spaces to tabs" )
        spacesToTabs.connect( "activate", exit )

        subMenuSpaces.append( drawSpaces )
        subMenuSpaces.append( indentOnTab )
        subMenuSpaces.append( autoIndent )
        subMenuSpaces.append( indentSpaces )
        subMenuSpaces.append( gtk.SeparatorMenuItem() )
        subMenuSpaces.append( incrTabWidth )
        subMenuSpaces.append( gtkWindow.tabWidth )
        subMenuSpaces.append( decrTabWidth )
        subMenuSpaces.append( gtk.SeparatorMenuItem() )
        subMenuSpaces.append( tabsToSpaces )
        subMenuSpaces.append( spacesToTabs )

        menuLang = gtk.MenuItem( "language?" )
        subMenuLang = gtk.Menu()
        menuLang.set_submenu( subMenuLang )

        openAllAs = gtk.MenuItem( "Open all file as..." )
        openAllAs.connect( "activate", exit ) # TODO

        # TODO list all languages activatable...
        subMenuLang.append( openAllAs )
        subMenuLang.append( gtk.SeparatorMenuItem() )
        # subMenuLang.append(tabsToSpaces)
        menub.append( menuLang )
        menub.append( menuSpaces )

        self.feedback = gtk.Label( "Ready" )

        self.pack_start( self.feedback, False, False, 10 )
        self.pack_end( menub, False, False, 0 )
        self.pack_end( gtk.VSeparator(), False, False, 0 )

    def statusbarView(self, widget):
        if widget.active:
            self.show()
        else:
            self.hide()

    def push(self, str):
        if str:
            self.feedback.set_text(str)
        else:
            return False

    def enable(self):
        self.show()

    def disable(self):
        self.hide()