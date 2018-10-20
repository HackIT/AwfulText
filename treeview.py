#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, os, stat, gobject, pango, re, config, time, gio, glib
from dialog import OpenFolderDialog

#gtk.STOCK_FILE gtk.STOCK_DIRECTORY gtk.STOCK_GO_FORWARD
#    def make_pb(self, tvcolumn, cell, model, iter):
#        stock = model.get_value(iter, 1)
#        pb = self.treeview.render_icon(stock, gtk.ICON_SIZE_MENU, None)
#        cell.set_property('pixbuf', pb)
#        return

def dbg(*vars):
    print vars

crossxpm = [
    "11 13 3 1",
    ", c #ffffff",
    ". c #777776",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@.@@@.@@@",
    "@@...@...@@",
    "@@,.....,@@",
    "@@@,...,@@@",
    "@@@.....@@@",
    "@@...,...@@",
    "@@,.,@,.,@@",
    "@@@,@@@,@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

folderxpm = [
    "15 14 3 1",
    "  c #ffffff",
    ". c #000000",
    "@ c None",
    "@@@@@@@@@@@@@@@",
    "@@....@@@@@@@@@",
    "@.    .@@@@@@@@",
    "@.     ......@@",
    "@.           .@",
    "@.           .@",
    "@.           .@",
    "@.           .@",
    "@.           .@",
    "@.           .@",
    "@.           .@",
    "@.           .@",
    "@@...........@@",
    "@@@@@@@@@@@@@@@"
    ]

filexpm = [
    "13 14 3 1",
    "  c #ffffff",
    ". c #000000",
    "@ c None",
    "@@@@@@@@@@@@@",
    "@@.......@@@@",
    "@.      ..@@@",
    "@.      . .@@",
    "@.      ....@",
    "@.         .@",
    "@.         .@",
    "@.         .@",
    "@.  . .    .@",
    "@. .   .   .@",
    "@.  . .    .@",
    "@.         .@",
    "@@.........@@",
    "@@@@@@@@@@@@@"
    ]

class TreeView( gtk.TreeView ):
    def __init__(self, treeModel):
        super( TreeView, self ).__init__(treeModel)

class TreeStore( gtk.TreeStore ):
    def __init__(self):
        super( TreeStore, self ).__init__( gtk.gdk.Pixbuf, gobject.TYPE_STRING )

class ListStore( gtk.ListStore ):
    def __init__(self):
        super( ListStore, self ).__init__( gtk.gdk.Pixbuf, gobject.TYPE_STRING )

class TreeViewColumn( gtk.TreeViewColumn ):
    def __init__(self):
        super( TreeViewColumn, self ).__init__()

class CellRendererPixbuf( gtk.CellRendererPixbuf ):
    def __init__(self):
        super( CellRendererPixbuf, self ).__init__()

class CellRendererText( gtk.CellRendererText ):
    def __init__(self):
        super( CellRendererText, self ).__init__()

class Menu( gtk.Menu ):
    def __init__(self):
        super( Menu, self ).__init__()

class MenuItem( gtk.MenuItem ):
    def __init__(self, name):
        super( MenuItem, self ).__init__(name)
        self.show()

class FileBrowser( gtk.VBox ):
    store = [] # treeStore's (iterPath, filePath)
    headers = [(0,)] # keep track of growing openfile list and put OPEN FOLDER header at end of it.
    openedFolders = [] # to make life easier when looking for file...
    monitoredFolders = [] # glib's monitoring storage... doesn't work without storing it.
    file_monitor_changed_type = None

# glib inotify monitoring
    def monitor(self, directory):
        directory = gio.File(directory)
        monitoredDir = directory.monitor_directory()
        monitoredDir.set_rate_limit(0)
        monitoredDir.connect("changed", self.monitorEvent)
        self.monitoredFolders.append(monitoredDir)

    # gio.FILE_MONITOR_EVENT_ATTRIBUTE_CHANGED
    # gio.FILE_MONITOR_EVENT_CHANGED
    # gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT
    # gio.FILE_MONITOR_EVENT_CREATED
    # gio.FILE_MONITOR_EVENT_DELETED
    # gio.FILE_MONITOR_EVENT_MOVED
    # gio.FILE_MONITOR_EVENT_PRE_UNMOUNT
    # gio.FILE_MONITOR_EVENT_UNMOUNTED
    # gio.FILE_MONITOR_NONE
    # gio.FILE_MONITOR_SEND_MOVED
    # gio.FILE_MONITOR_WATCH_HARD_LINKS
    # gio.FILE_MONITOR_WATCH_MOUNTS
    def monitorEvent(self, dirMon, fileMon, event, monitorEvent):
        if monitorEvent == gio.FILE_MONITOR_EVENT_CREATED:
            self.file_monitor_changed_type = gio.FILE_MONITOR_EVENT_CREATED
        elif monitorEvent == gio.FILE_MONITOR_EVENT_DELETED:
            tpath = self.storeLook(fileMon.get_path())
            if self.treeStore.iter_is_valid(tpath):
                self.treeStore.remove(tpath)
        elif monitorEvent == gio.FILE_MONITOR_EVENT_CHANGED:
            self.file_monitor_changed_type = gio.FILE_MONITOR_EVENT_CHANGED
        elif monitorEvent == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
            # this is last call for moving/creating file, proceed here, clean...
            #if self.file_monitor_changed_type == gio.FILE_MONITOR_EVENT_CREATED:
                # add file to treeview
            #elif self.file_monitor_changed_type == gio.FILE_MONITOR_EVENT_CHANGED:
                # 
            self.file_monitor_changed_type = None
        print dirMon, fileMon.get_path()

    def storeLook(self, filepath):
        for n in self.store:
            if filepath in n:
                return n[0]


# treeview cell properties
    def propertiesIcon(self, column, cell, liststore, iter):
        cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        cell.props.sensitive = True
        # for cells that acts as hearders
        for head in self.headers:
            if liststore.get_path(iter) == head:
                cell.set_property("visible", False)
                return
        cell.set_property("visible", True)
        cell.set_property("pixbuf", self.delete_pixbuf)

    def propertiesText(self, column, cell, liststore, iter):
        value = liststore[iter]
        # default cell layout style
        cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        cell.props.sensitive = True
        cell.props.weight = pango.WEIGHT_NORMAL
        # for cells that acts as hearders
        for head in self.headers:
            if liststore.get_path(iter) == head:
                cell.props.mode = gtk.CELL_RENDERER_MODE_INERT
                #cell.props.sensitive = False
                cell.props.weight = pango.WEIGHT_BOLD


# treeview selection callbacks
    def onSelectListStore(self, path, listSelection):
        # disable highlight in liststore headers
        for head in self.headers:
            if path == head:
                return False
        return True

    def onSelectTreeStore(self, path, treeSelection):
        # disable highlight dirs
        if self.treeStore.iter_has_child(self.treeStore.get_iter(path)):
            return False
        return True

    def onTreeSelection(self, treeSelection):
        def getValue(row,column):
            return self.treeStore.get_value(row, column)

        treeModel, treeIter = treeSelection.get_selected()
        if treeIter == None: return
        column = 1
        fpath = []
        # file handling
        if not self.treeStore.iter_has_child(treeIter):
            filename = '%s' % (getValue(treeIter, column))
            fpath.append(filename)
            while treeIter != None:
                 treeIter = self.treeStore.iter_parent(treeIter)
                 if treeIter:
                     fpath.append('%s' % (getValue(treeIter, column)))
            filepath = ''.join(['/%s' % (v) for v in fpath.__reversed__()])
            if not os.path.isdir(filepath) and not os.path.isfile(filepath):
                for v in self.openedFolders:
                    if os.path.isfile(v+filepath):
                        self.Window.buffer.showFile(v+filepath)
        return

# openig files
    def renderFolder(self, folder):
        def exclude(filename):
            for i in config.ignore:
                if re.search('\\'+i+'$', filename):
                    return False
            return True

        if folder:
            if len(self.headers) < 2:
                self.headers.append( self.listStore.get_path( self.listStore.append([None, 'FOLDERS']) ) )
            self.openedFolders.append(folder)
            self.monitor(folder)
            files = [f for f in os.listdir(folder) if f[0] <> '.']
            nextpath = []
            if files:
                for f in files:
                    fpath = os.path.join(folder, f)
                    if os.path.isdir(fpath):
                        self.monitor(fpath)
                        self.openedFolders.append(fpath)
                        tpath = self.treeStore.append(None, [self.folder_pixbuf, f])
                        nextpath.append( (tpath, fpath) )
                        self.store.append( (tpath, fpath) )
                    else:
                        if exclude(f):
                            tpath = self.treeStore.append(None, [self.file_pixbuf, f])
                            self.store.append( (tpath, fpath) )
                while nextpath:
                    c = nextpath.pop(0)
                    for s in os.listdir(c[1]):
                        fpath = os.path.join(c[1], s)
                        if os.path.isdir( fpath ):
                            self.monitor(fpath)
                            self.openedFolders.append(fpath)
                            tpath = self.treeStore.append(c[0], [self.folder_pixbuf,s])
                            nextpath.append( (tpath, fpath) )
                            self.store.append( (tpath, fpath) )
                        else:
                            if exclude(s):
                                tpath = self.treeStore.append(c[0], [self.file_pixbuf, s])
                                self.store.append( (tpath, fpath) )
            print self.openedFolders.__len__(), "\n", self.monitoredFolders.__len__(), self.store.__len__()

    def addFolder(self, ImageMenuItem=None):
        dialog = OpenFolderDialog()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            dialog.destroy()
            if filename:
                self.renderFolder(filename)
        else:
            dialog.destroy()

    def openFolder(self, ImageMenuItem):
        self.treeStore.clear()
        self.addFolder()

# menu callback
    def newFileSelection(self, menuItem, path):
        # check for folder and file
        print self, treeView, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def newFolderSelection(self, menuItem, path):
        # check for folder and file
        print self, treeView, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def renameSelection(self, menuItem, path):
        # check for folder and file
        print self, treeView, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def deleteSelection(self, menuItem, path):
        # check for folder and file
        print self, menuItem, path
        if path:
            iter = self.treeStore.get_iter(path)
            if self.treeStore.iter_is_valid(iter):
                filepath = self.reversePath(iter)
                if os.path.isdir(filepath):
                    os.removedirs(filepath)
                elif os.path.isfile(filepath):
                    os.remove(filepath)
                #self.treeStore.remove(iter)

    def openFolderSelection(self, menuItem, path):
        # shud open system's file browser... config?/auto?
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def findSelection(self, menuItem, path):
        # print self, menuItem, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def reversePath(self, iter):
        fpath = []
        filename = '%s' % self.treeStore.get_value(iter, 1)
        fpath.append(filename)
        while iter != None:
             iter = self.treeStore.iter_parent(iter)
             if iter:
                 fpath.append('%s' % self.treeStore.get_value(iter, 1))
        filepath = ''.join(['/%s' % (v) for v in fpath.__reversed__()])
        for v in self.openedFolders:
            if v == '/':
                if os.path.exists(filepath):
                    break
            if os.path.exists(v+filepath):
                filepath = v+filepath
                break
        return filepath

# treeview menus
    def treeMenu(self, treeView, event):
        if self.headers.__len__() == 2:
            path = treeView.get_path_at_pos(int(event.x), int(event.y))[0]
            selectedIter = self.treeStore.get_iter(path)
            filepath = self.reversePath(selectedIter)
            if event.button == 3 and os.path.isfile(filepath): # right clik on file
                self.contextMenu( [{'name':'rename', 'activate':self.renameSelection, 'path':path, 'event':event },
                    {'name':'delete', 'activate':self.deleteSelection, 'path':path, 'event':event },
                    {'name':'open containing folder', 'activate':self.openFolderSelection, 'path':path, 'event':event }] )
            elif event.button == 3 and os.path.isdir(filepath): # right clik on dir
                self.contextMenu( [ {'name':'rename', 'activate':self.renameSelection, 'path':path, 'event':event },
                    {'name':'new file', 'activate':self.newFileSelection, 'path':path, 'event':event },
                    {'name':'new folder', 'activate':self.newFolderSelection, 'path':path, 'event':event },
                    {'name':'delete folder', 'activate':self.deleteSelection, 'path':path, 'event':event },
                    {'name':'find in folder', 'activate':self.findSelection, 'path':path, 'event':event } ] )
            #selectedIter = self.treeStore.get_iter(path)
            #print path, self.treeStore.get_value(selectedIter, 1), event


# listStore menu
    def closeSelection(self, menuItem, path):
        # print self, menuItem, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def listMenu(self, treeView, event):
        # here shud be all open files... might change cuz textview's topbar
        if treeView.get_path_at_pos(int(event.x), int(event.y)):
            path = treeView.get_path_at_pos(int(event.x), int(event.y))[0]
            for header in self.headers:
                if path == header:
                    return False
            if event.button == 3: # right clik
                self.contextMenu( [{'name':'close', 'activate':self.closeSelection, 'path':path, 'event':event }] )
            #selectedIter = self.listStore.get_iter(path)
            #print path, self.listStore.get_value(selectedIter, 1), event

    def contextMenu(self, menuItems):
        # this way cuz catching menu state to remove menu items... may change...
        for i in [None, Menu()]: # pretty strange to me but it's okay for now
            self.menu = i # to have dynamic parameter...
        for m in menuItems:
            menuItem = MenuItem(m['name'])
            menuItem.connect('activate', m['activate'], m['path'])
            self.menu.add(menuItem)
        self.menu.popup(None, None, None, m['event'].button, m['event'].time)

    def __init__(self, gtkWindow):
        super( FileBrowser, self ).__init__()
        self.current_directory = os.getcwd()
        self.Window = gtkWindow

        # create liststore
        self.listStore = ListStore()
        self.treeStore = TreeStore()

        # create the TreeView using ListStore
        treeViewList = TreeView(self.listStore)
        treeViewList.connect( "button-press-event", self.listMenu )
        treeViewList.set_headers_visible(False)
        treeViewList.set_enable_search(False)
        # disable FOCUS selection
        treeViewList.unset_flags(gtk.CAN_FOCUS)
        # create the TreeView using TreeStore
        treeViewTree = TreeView(self.treeStore)
        treeViewTree.connect( "button-press-event", self.treeMenu )
        treeViewTree.set_headers_visible(False)
        treeViewTree.set_enable_search(False)
        treeViewTree.unset_flags(gtk.CAN_FOCUS)
        #self.TreeViewTreeSelection = self.TreeViewTree.get_selection()
        #self.TreeViewTreeSelection.set_mode( gtk.SELECTION_SINGLE)
        #self.TreeViewList.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        #self.TreeViewList.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#000000"))
        #self.TreeViewTree.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        #self.TreeViewTree.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#000000"))

        self.delete_pixbuf = gtk.gdk.pixbuf_new_from_xpm_data( crossxpm )

        if config.icon_theme == False:
            self.file_pixbuf = gtk.gdk.pixbuf_new_from_xpm_data( filexpm )
            self.folder_pixbuf = gtk.gdk.pixbuf_new_from_xpm_data( folderxpm )
        else:
            self.folder_pixbuf = self.TreeViewTree.render_icon(
                gtk.STOCK_DIRECTORY,
                gtk.ICON_SIZE_MENU, None)
            self.file_pixbuf = self.TreeViewTree.render_icon(
                gtk.STOCK_FILE,
                gtk.ICON_SIZE_MENU, None)

        # TODO openfiles
        self.listStore.append([None, "OPENFILES"])
        self.listStore.append([None, "somefile"])

        # create a CellRenderers to render the data
        cellRendererPixbufList = CellRendererPixbuf()
        cellRendererTextList = CellRendererText()
        cellRendererTextTree = CellRendererText()
        cellRendererPixbufTree = CellRendererPixbuf()

        treeViewColumnList = TreeViewColumn()

        # add the cells to the columns - 2 in the first
        treeViewColumnList.pack_start( cellRendererPixbufList, False )
        treeViewColumnList.pack_start( cellRendererTextList, False )
        
        #treeViewColumnList.set_attributes(cellRendererPixbufList, stock_id=0)
        treeViewColumnList.set_attributes(cellRendererTextList, text=1)
        
        treeViewColumnList.set_cell_data_func(cellRendererTextList, self.propertiesText)
        treeViewColumnList.set_cell_data_func(cellRendererPixbufList, self.propertiesIcon)

        treeViewList.append_column(treeViewColumnList)

        treeViewColumnTree = gtk.TreeViewColumn()
        treeViewColumnTree.pack_start( cellRendererPixbufTree, False)
        treeViewColumnTree.pack_start(cellRendererTextTree, False)
        #treeViewColumnTree.set_cell_data_func(cellRendererPixbufTree, self.fsicon)
        treeViewColumnTree.set_attributes(cellRendererPixbufTree, pixbuf=0)
        treeViewColumnTree.set_attributes(cellRendererTextTree, text=1)
        #treeViewColumnTree.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        #treeViewColumnTree.set_cell_data_func(cellRendererPixbufTree, self.fsicon)
        # add columns to treeview
        treeViewTree.append_column(treeViewColumnTree)

        treeSelectionList = treeViewList.get_selection()
        #treeSelection.connect( 'changed', callme )
        treeSelectionList.set_select_function(self.onSelectListStore, treeSelectionList)
        
        treeSelectionTree = treeViewTree.get_selection()
        #treeViewTree.connect( 'row-activated', self.rowactivated )
        treeSelectionTree.set_select_function(self.onSelectTreeStore, treeSelectionTree)
        treeSelectionTree.connect('changed', self.onTreeSelection)
        #treeViewTreeSelection.
        self.pack_start(treeViewList, False)
        self.pack_start(treeViewTree, True)
