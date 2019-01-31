#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, os, stat, gobject, pango, re, config, time, gio, glib
from dialog import OpenFolderDialog, NewFileEntry

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
    "@@.......@@",
    "@@@.....@@@",
    "@@@.....@@@",
    "@@.......@@",
    "@@...@...@@",
    "@@@.@@@.@@@",
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

class HeadView( gtk.TreeView ):
    def __init__(self):
        super( HeadView, self ).__init__(gtk.ListStore(gobject.TYPE_STRING))
        self.set_headers_visible(False)
        self.set_enable_search(False)
        # disable FOCUS selection
        self.unset_flags(gtk.CAN_FOCUS)
        self.selection = self.get_selection()
        self.selection.set_mode(gtk.SELECTION_NONE)


class TreeView( gtk.TreeView ):
    def __init__(self, treeModel):
        super( TreeView, self ).__init__(treeModel)
        self.set_headers_visible(False)
        self.set_enable_search(False)
        # disable FOCUS selection
        self.unset_flags(gtk.CAN_FOCUS)
        self.selection = self.get_selection()
        self.selection.set_mode(gtk.SELECTION_SINGLE)

class CellView( gtk.CellView ):
    def __init__(self):
        super( CellView, self ).__init__()

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
        self.props.mode = gtk.CELL_RENDERER_MODE_INERT
        self.props.sensitive = True

class CellRendererText( gtk.CellRendererText ):
    def __init__(self):
        super( CellRendererText, self ).__init__()
        self.props.mode = gtk.CELL_RENDERER_MODE_INERT
        self.props.sensitive = True
        self.props.weight = pango.WEIGHT_NORMAL

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
    openedFiles = []
    monitoredFolders = [] # glib's monitoring storage... doesn't work without storing it.
    file_monitor_changed_type = None

# glib inotify monitoring
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
    def monitor(self, directory):
        directory = gio.File(directory)
        monitoredDir = directory.monitor_directory()
        monitoredDir.set_rate_limit(0)
        monitoredDir.set_data("path", directory)
        monitoredDir.connect("changed", self.monitorEvent)
        self.monitoredFolders.append(monitoredDir)
        print self.monitoredFolders.__len__(), monitoredDir.get_data("path").get_path()

    def monitorEvent(self, dirMon, fileMon, event, monitorEvent):
        if monitorEvent == gio.FILE_MONITOR_EVENT_CREATED:
            self.file_monitor_changed_type = gio.FILE_MONITOR_EVENT_CREATED
            # root tree
            treepath = self.storeLook(dirMon.get_data("path").get_path())
            if os.path.isdir(fileMon.get_path()):
                tpath = self.treeStore.append(treepath, [self.folder_pixbuf, os.path.basename(fileMon.get_path())])
            else:
                tpath = self.treeStore.append(treepath, [self.file_pixbuf, os.path.basename(fileMon.get_path())])
            self.store.append( (tpath, fileMon.get_path()) )
        elif monitorEvent == gio.FILE_MONITOR_EVENT_DELETED:
            tpath = self.storeLook(fileMon.get_path())
            if self.treeStore.iter_is_valid(tpath):
                self.treeStore.remove(tpath)
                #print self.treeStore.get_path(tpath), self.treeStore.get_value(tpath, 1)
        elif monitorEvent == gio.FILE_MONITOR_EVENT_CHANGED:
            self.file_monitor_changed_type = gio.FILE_MONITOR_EVENT_CHANGED
        elif monitorEvent == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
            # this seemed like the last call for moving/creating file, but afaik
            self.file_monitor_changed_type = None
        print dirMon, fileMon.get_path(), monitorEvent

    def disableDirMonitor(self, filepath):
        for i in self.monitoredFolders:
            if filepath == i.get_data("path").get_path():
                i.cancel()
                ret = i.is_cancelled()
                self.monitoredFolders.remove(i)
        return None

    def storeLook(self, filepath):
        for n in self.store:
            if filepath in n:
                return n[0]

# treeview cell properties
    def propertiesIcon(self, column, cell, liststore, iter):
        # for cells that acts as hearders
        for head in self.headers:
            if liststore.get_path(iter) == head:
                cell.set_property("visible", False)
                return
        cell.set_property("visible", True)
        cell.set_property("pixbuf", self.delete_pixbuf)

    def propertiesText(self, column, cell, liststore, iter):
        # value = liststore[iter]
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
        filepath = self.reversePathFromIter(self.treeStore.get_iter(path))
        if os.path.isdir(filepath):
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
                        self.Window._openFile(v+filepath)
        return

    def listInsert(self,filename):
        if self.headers.__len__() == 2:
            path = self.headers[1]
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.insert_before(iter, [None, os.path.basename(filename)])
                print "inserted", iter
        else: # No opened folder just append...
            self.listStore.append([None, os.path.basename(filename)])
            print "no opened folder just append"

# opening/adding files
    def renderFolder(self, folder):
        def exclude(filename):
            for i in config.ignore:
                if re.search('\\'+i+'$', filename):
                    return False
            return True
        if folder and folder in self.openedFolders:
            return
        if len(self.headers) < 2:
            self.headers.append( self.listStore.get_path( self.listStore.append([None, 'FOLDERS']) ) )
        self.openedFolders.append(folder)
        self.monitor(folder)
        files = [f for f in os.listdir(folder)] # if f[0] <> '.'
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
                    if os.path.isdir(fpath):
                        self.monitor(fpath)
                        self.openedFolders.append(fpath)
                        tpath = self.treeStore.append(c[0], [self.folder_pixbuf,s])
                        nextpath.append( (tpath, fpath) )
                        self.store.append( (tpath, fpath) )
                    else:
                        if exclude(s):
                            tpath = self.treeStore.append(c[0], [self.file_pixbuf, s])
                            self.store.append( (tpath, fpath) )
        print self.openedFolders.__len__(), self.monitoredFolders.__len__(), self.store.__len__()

    def clearTreeStore(self):
        self.treeStore.clear()
        while self.openedFolders:
            dirmonitor = self.openedFolders.pop()
            self.disableDirMonitor(dirmonitor)
            self.store = []
        #self.addFolder()

# menus callback
    def newFileSelection(self, treeView, path):
        print self, treeView, path
        if path:
            iter = self.treeStore.get_iter(path)
            if self.treeStore.iter_is_valid(iter):
                filepath = self.reversePathFromIter(iter)
                print self.openedFolders, filepath
                # CHECKKKKKKKKKKKKKK
                self.Window._openFile(self, filepath)
                # just open new file to buffer...
                # also store path for ez saving from where it's meant
                #NewFileEntry()
                #if os.path.isdir(filepath):
                #    open()

    def newFolderSelection(self, menuItem, path):
        print self, menuItem, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def renameSelection(self, menuItem, path):
        print self, menuItem, path
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def deleteSelection(self, menuItem, path):
        # deleting from tree
        #print self, menuItem, path
        dirs = []
        delete = []
        if path:
            iter = self.treeStore.get_iter(path)
            if self.treeStore.iter_is_valid(iter):
                filepath = self.reversePathFromIter(iter)
                self.disableDirMonitor(filepath)
                if os.path.isdir(filepath):
                    delete.append(filepath)
                    if self.treeStore.iter_has_child(iter):
                        files = os.listdir(filepath)
                        for f in files:
                            fpath = os.path.join(filepath, f)
                            if os.path.isdir(fpath):
                                dirs.append(fpath)
                            else:
                                delete.append(fpath)
                        while dirs:
                            path = dirs.pop(0)
                            delete.append(path)
                            for f in os.listdir(path):
                                fpath = os.path.join(path, f)
                                if os.path.isdir( fpath ):
                                    dirs.append(fpath)
                                else:
                                    delete.append(fpath)
                        #delete.reverse()
                        #print delete
                        for f in delete.__reversed__():
                            if os.path.isdir(f):
                                self.disableDirMonitor(f) # skip monitoring
                                os.removedirs(f)
                            else:
                                os.remove(f)
                elif os.path.isfile(filepath):
                    os.remove(filepath)
                #self.treeStore.remove(iter)

    def openFolderSelection(self, menuItem, path):
        # shud open system's file browser... config?/auto?
        if path:
            iter = self.treeStore.get_iter(path)
            if self.treeStore.iter_is_valid(iter):
                filepath = self.reversePathFromIter(iter)
                os.popen4(config.file_browser+" "+filepath)

    def findSelection(self, menuItem, path):
        if path:
            iter = self.listStore.get_iter(path)
            if self.listStore.iter_is_valid(iter):
                self.listStore.remove(iter)

    def reversePathFromIter(self, iter):
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

# treeStore menus
    def treeMenu(self, treeView, event):
        if self.headers.__len__() == 2:
            path = treeView.get_path_at_pos(int(event.x), int(event.y))[0]
            selectedIter = self.treeStore.get_iter(path)
            filepath = self.reversePathFromIter(selectedIter)
            if event.button == 3 and os.path.isfile(filepath): # right clik on file
                self.contextMenu( [{'name':'rename', 'activate':self.renameSelection, 'path':path, 'event':event },
                {'name':'delete', 'activate':self.deleteSelection, 'path':path, 'event':event },
                {'name':'open containing folder', 'activate':self.openFolderSelection, 'path':path, 'event':event }] )
            elif event.button == 3 and os.path.isdir(filepath): # right clik on dir
                self.contextMenu( [ {'name':'rename', 'activate':self.renameSelection, 'path':path, 'event':event },
                    {'name':'new file', 'activate':self.newFileSelection, 'path':path, 'event':event },
                    {'name':'new folder', 'activate':self.newFolderSelection, 'path':path, 'event':event },
                    {'name':'open filebrowser', 'activate':self.openFolderSelection, 'path':path, 'event':event },
                    {'name':'delete folder', 'activate':self.deleteSelection, 'path':path, 'event':event },
                    {'name':'find in folder', 'activate':self.findSelection, 'path':path, 'event':event } ] )
            #selectedIter = self.treeStore.get_iter(path)
            #print path, self.treeStore.get_va0lue(selectedIter, 1), event

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

#
    def __init__(self, gtkWindow):
        super( FileBrowser, self ).__init__()
        self.current_directory = os.getcwd()
        self.Window = gtkWindow

        # listStore handles open files
        self.listStore = ListStore()
        # treeStore handles folder trees
        self.treeStore = TreeStore()

        # create the TreeView using ListStore
        treeViewList = TreeView(self.listStore)
        treeViewList.connect( "button-press-event", self.listMenu )
        
        # create the TreeView using TreeStore
        treeViewTree = TreeView(self.treeStore)
        treeViewTree.connect( "button-press-event", self.treeMenu )

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
        cellRendererPixbufList.set_property("follow-state", True)

        cellRendererTextList = CellRendererText()

        cellRendererPixbufTree = CellRendererPixbuf()
        cellRendererTextTree = CellRendererText()
        # LIST
        treeViewColumnList = TreeViewColumn()

        # add the cells to the columns - 2 in the first
        treeViewColumnList.pack_start( cellRendererPixbufList, expand=False )
        treeViewColumnList.pack_start( cellRendererTextList, expand=False )
        
        #treeViewColumnList.set_attributes(cellRendererPixbufList, stock_id=0)
        treeViewColumnList.set_attributes(cellRendererTextList, text=1)
        
        treeViewColumnList.set_cell_data_func(cellRendererTextList, self.propertiesText)
        treeViewColumnList.set_cell_data_func(cellRendererPixbufList, self.propertiesIcon)

        treeViewList.append_column(treeViewColumnList)
        # TREE
        treeViewColumnTree = gtk.TreeViewColumn()
        treeViewColumnTree.pack_start(cellRendererPixbufTree, expand=False)
        treeViewColumnTree.pack_start(cellRendererTextTree, expand=False)

        treeViewColumnTree.set_attributes(cellRendererPixbufTree, pixbuf=0)
        treeViewColumnTree.set_attributes(cellRendererTextTree, text=1)
        # add columns to treeview
        treeViewTree.append_column(treeViewColumnTree)

        treeViewList.selection.set_select_function(self.onSelectListStore, treeViewList.selection)
        
        treeViewTree.selection.set_select_function(self.onSelectTreeStore, treeViewTree.selection)
        treeViewTree.selection.connect('changed', self.onTreeSelection)
        #treeViewTreeSelection.

        self.pack_start(treeViewList, False)
        self.pack_start(treeViewTree, True)
