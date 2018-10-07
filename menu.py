import pygtk
pygtk.require('2.0')
import gtk, config, tools

from dialog import About

# File                View                              Tools                    Help
#   | ---> NewFile      | ---> Show menubar               | ---> build             | ---> about
#   | ---> OpenFile     | ---> Show statusbar             | ---> colorpicker
#   | ---> SaveFile     | ---> Show sidebar
#   | ---> SaveAs       | ---> Show console
#   | ---> Quit         | ---> Show line numbers
#                       | ---> Highlight current line
#
# TODO -
# : open recent file

class Menubar( gtk.MenuBar ):
    def __init__( self, gtkWindow ):
        super( Menubar, self ).__init__()
        menuFile = gtk.MenuItem( "_File" )
        menuFileItem = gtk.Menu()
        menuFile.set_submenu( menuFileItem )

        menuFileItem.append( self.menuPush( gtk.STOCK_NEW, "<Control>N", gtkWindow.buffer.newFile, gtkWindow ) )
        menuFileItem.append( self.menuPush( gtk.STOCK_OPEN, "<Control>O", gtkWindow.buffer.openFile, gtkWindow ) )
        
        openFolder = gtk.MenuItem( "Open Folder" )
        openFolder.connect( "activate", gtkWindow.filebrowser.openFolder )
        menuFileItem.append( openFolder )

        addFolder = gtk.MenuItem( "Add Folder" )
        addFolder.connect( "activate", gtkWindow.filebrowser.addFolder )
        menuFileItem.append( addFolder )

        #menuFileItem.append( self.menuPush( gtk.STOCK_OPEN, "Open folder...", gtkWindow.filebrowser.openFolder, gtkWindow ) )
        menuFileItem.append( self.menuPush( gtk.STOCK_SAVE, "<Control>S", gtkWindow.buffer.save, gtkWindow ) )
        menuFileItem.append( self.menuPush( gtk.STOCK_SAVE_AS, "<Shift><Control>S", gtkWindow.buffer.save_as, gtkWindow ) )
        menuFileItem.append( gtk.SeparatorMenuItem() )
        menuFileItem.append( self.menuPush( gtk.STOCK_QUIT, "<Control>Q", gtkWindow.mainQuit, gtkWindow ) )

        menuView = gtk.MenuItem( "_View" )
        menuViewItem = gtk.Menu()
        menuView.set_submenu( menuViewItem )

        showMenubar = gtk.CheckMenuItem( "Show Menubar" )
        showMenubar.set_active( config.window_menu )
        showMenubar.connect( "activate", self.menubarView )
        menuViewItem.append( showMenubar )

        showStatusbar = gtk.CheckMenuItem( "Show Statusbar" )
        showStatusbar.set_active( config.window_statusbar )
        showStatusbar.connect( "activate", gtkWindow.statusbar.statusbarView )
        menuViewItem.append( showStatusbar )
        
        menuViewItem.append( gtk.SeparatorMenuItem() )
        
        showDirBrowser = gtk.CheckMenuItem( "Show Sidebar" )
        showDirBrowser.set_active( config.window_sidepane )
        showDirBrowser.connect( "activate", gtkWindow.toggleFileBrowser )
        menuViewItem.append( showDirBrowser )

        showConsole = gtk.CheckMenuItem( "Show Console" )
        showConsole.set_active( config.window_console )
        showConsole.connect( "activate", gtkWindow.toggleConsole )
        menuViewItem.append( showConsole )

        menuViewItem.append( gtk.SeparatorMenuItem() )

        showLineNumbers = gtk.CheckMenuItem( "Show line numbers" )
        showLineNumbers.set_active( config.show_line_numbers )
        showLineNumbers.connect( "activate", gtkWindow.view.toggleLineNumbers )
        menuViewItem.append( showLineNumbers )

        highlightCurrentLine = gtk.CheckMenuItem( "Highlight current line" )
        highlightCurrentLine.set_active( config.highlight_current_line )
        highlightCurrentLine.connect( "activate", gtkWindow.view.toggleHighlightCurrentLine )
        menuViewItem.append( highlightCurrentLine )

        menuTools = gtk.MenuItem( "_Tools" )
        menuToolsItem = gtk.Menu()
        menuTools.set_submenu( menuToolsItem )
        menuToolsItem.append( self.menuPush( "Build", "<Control>B", exit, gtkWindow ) )
        menuToolsItem.append( self.menuPush( "ColorPicker", "<Control>F", tools.ColorDial, gtkWindow ) )
        #buildTool = gtk.MenuItem( "build" )
        #buildTool.connect( "activate", exit )
        #menuToolsItem.append( buildTool )

        menuHelp = gtk.MenuItem( "_Help" )
        menuHelpItem = gtk.Menu()
        menuHelp.set_submenu( menuHelpItem )

        aboutDial = gtk.MenuItem( "about" )
        aboutDial.connect( "activate", About )
        menuHelpItem.append( aboutDial )

        self.append( menuFile )
        self.append( menuView )
        self.append( menuTools )
        self.append( menuHelp )

    def menuPush( self, strdata, binding, activate, gtkWindow ):
        accelGroup = gtk.AccelGroup()
        gtkWindow.add_accel_group( accelGroup )
        menuItem = gtk.ImageMenuItem( strdata, accelGroup )
        key, mod = gtk.accelerator_parse( binding )
        menuItem.add_accelerator( "activate",
            accelGroup, key, mod, gtk.ACCEL_VISIBLE
        )
        if activate:
            menuItem.connect( "activate", activate )
        return menuItem

    def menuCreate(self, name):
        menu = gtk.MenuItem(name)
        subMenu = gtk.Menu()
        menu.set_submenu(subMenu)
        return menu, subMenu

    def menubarView(self, checkMenuItem):
        if checkMenuItem.active:
            self.enable()
        else:
            self.disable()
    
    def enable(self):
        self.show()

    def disable(self):
        self.hide()
