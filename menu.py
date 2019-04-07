#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, config

from dialog import About, ColorDial

(
 MENU_ITEM,
 IMAGE_MENU_ITEM,
 CHECK_MENU_ITEM,
 MENU_SEPARATOR
) = range (4)

# File                View                              Tools                    Help
#   | ---> NewFile      | ---> Show menubar               | ---> build             | ---> about
#   | ---> OpenFile     | ---> Show statusbar             | ---> colorpicker
#   | ---> OpenFolder   | ---> Show sidebar
#   | ---> AddFolder    | ---> Show console
#   | ---> Save         | ---> Show line numbers
#   | ---> SaveAs       | ---> Highlight current line
#   | ---> Quit

# TODO -
# : open recent file

class Menubar( gtk.MenuBar ):
    def __init__( self, gtkWindow ):
        super( Menubar, self ).__init__()

        # type:
        # 0 == gtk.MenuItem
        # 1 == gtk.ImageMenuItem
        # 2 == gtk.CheckMenuItem
        # 3 == gtk.SeparatorMenuItem()
        menus = [ \
            {
            'menu_label':"_File",
            'menu_items':[
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_NEW,
                    'label':'New File',
                    'binding':"<Control>N",
                    'activate': gtkWindow.newFile
                },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_OPEN,
                    'label':'Open File',
                    'binding':"<Control>O",
                    'activate': gtkWindow.openFile
                },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_OPEN,
                    'label':'Open Folder',
                    'binding':None,
                    'activate': gtkWindow.openFolder
                },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_ADD,
                    'label':'Add Folder',
                    'binding':None,
                    'activate': gtkWindow.addFolder
                },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_SAVE,
                    'label':'Save',
                    'binding':'<Control>S',
                    'activate': gtkWindow.save
                },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_SAVE_AS,
                    'label': 'Save As',
                    'binding':'<Shift><Control>S',
                    'activate': gtkWindow.saveAs
                },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_CLOSE,
                    'label': 'Close file',
                    'binding':'<Control>W',
                    'activate': gtkWindow.close
                },
                {'type':MENU_SEPARATOR },
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_QUIT,
                    'label':"Quit",
                    'binding':"<Control>Q",
                    'activate': gtkWindow.mainQuit
                }
            ]},
            {
            'menu_label':"_View",
            'menu_items':[
                {
                    'type':CHECK_MENU_ITEM,
                    'label':"Show Menubar",
                    'is_active':config.window_menu,
                    'activate':self.menubarView
                },
                {
                    'type':CHECK_MENU_ITEM,
                    'label':"Show Statusbar",
                    'is_active':config.window_statusbar,
                    'activate':gtkWindow.statusbar.statusbarView
                },
                {'type':MENU_SEPARATOR },
                {
                    'type':CHECK_MENU_ITEM,
                    'label':"Show Side pane",
                    'is_active':config.window_sidepane ,
                    'activate':gtkWindow.toggleFolderTree
                },
                {
                    'type':CHECK_MENU_ITEM,
                    'label':"Show Console",
                    'is_active':config.window_console ,
                    'activate':gtkWindow.toggleConsole
                },
                {'type':MENU_SEPARATOR },
                {
                    'type':CHECK_MENU_ITEM,
                    'label':"Show line numbers",
                    'is_active':config.show_line_numbers ,
                    'activate':gtkWindow.view.toggleLineNumbers
                },
                {
                    'type':CHECK_MENU_ITEM,
                    'label':"Highlight current line",
                    'is_active':config.highlight_current_line ,
                    'activate':gtkWindow.view.toggleHighlightCurrentLine
                }
            ]},
            {
            'menu_label':"_Tools",
            'menu_items':[
                {
                    'type':MENU_ITEM,
                    'label':'Build',
                    'binding':'<Control>B',
                    'activate': exit
                },
                {
                    'type':MENU_ITEM,
                    'label':'ColorPicker',
                    'binding':'<Control>F',
                    'activate':ColorDial
                }
            ]},
            {
            'menu_label':"_Help",
            'menu_items':[
                {
                    'type':IMAGE_MENU_ITEM,
                    'stockId':gtk.STOCK_ABOUT,
                    'label':"About",
                    'binding':None,
                    'activate':About
                }
            ]}
        ]

        for i in menus: # root menus
            menu_label = gtk.MenuItem( i['menu_label'] )
            menu_label_items = gtk.Menu()
            menu_label.set_submenu( menu_label_items )
            for n in i['menu_items']:
                menu_item = None
                if n['type'] == MENU_SEPARATOR: # gtk.SeparatorMenuItem
                    menu_label_items.append( gtk.SeparatorMenuItem() )
                    continue

                if n['type'] == CHECK_MENU_ITEM: # gtk.CheckMenuItem
                    menu_item = gtk.CheckMenuItem( n['label'] )
                    if n['is_active']:
                        menu_item.set_active( n['is_active'] )
                    if n['activate']:
                        menu_item.connect('activate', n['activate'])
                    menu_label_items.append(menu_item)
                    continue

                if n['type'] == IMAGE_MENU_ITEM: # gtk.ImageMenuItem
                    if n['stockId']:
                        menu_item = gtk.ImageMenuItem( n['stockId'] )
                        menu_item.set_label(n['label'])
                        if n['binding']:
                            menu_item.set_accel_group(gtkWindow.accelGroup)
                            key, mod = gtk.accelerator_parse( n['binding'] )
                            menu_item.add_accelerator( "activate",
                                gtkWindow.accelGroup, key, mod, gtk.ACCEL_VISIBLE
                            )
                        if n['activate']:
                            menu_item.connect('activate', n['activate'])
                    menu_label_items.append(menu_item)
                    continue

                if n['type'] == MENU_ITEM: # gtk.MenuItem
                    menu_item = gtk.MenuItem( n['label'] )
                    if n['binding']:
                        key, mod = gtk.accelerator_parse( n['binding'] )
                        menu_item.add_accelerator( "activate",
                            gtkWindow.accelGroup, key, mod, gtk.ACCEL_VISIBLE
                        )
                    if n['activate']:
                        menu_item.connect('activate', n['activate'])
                    menu_label_items.append(menu_item)
                    continue
            self.append(menu_label)

    def menubarView(self, checkMenuItem):
        if checkMenuItem.active:
            self.enable()
        else:
            self.disable()

    def enable(self):
        self.show()

    def disable(self):
        self.hide()
