#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, os, stat, gobject, pango, re, config, time, gio, glib, pixmap
from dialog import OpenFolderDialog, NewFileEntry

#gtk.STOCK_FILE gtk.STOCK_DIRECTORY gtk.STOCK_GO_FORWARD
#    def make_pb(self, tvcolumn, cell, model, iter):
#        stock = model.get_value(iter, 1)
#        pb = self.treeview.render_icon(stock, gtk.ICON_SIZE_MENU, None)
#        cell.set_property('pixbuf', pb)
#        return

def dbg(*vars):
    print vars

class TreeView( gtk.TreeView ):
    def __init__(self, treeModel):
        super( TreeView, self ).__init__(treeModel)
        self.set_headers_visible(False)
        self.set_enable_search(False)
        # disable FOCUS selection
        self.unset_flags(gtk.CAN_FOCUS)
        self.selection = self.get_selection()
        self.selection.set_mode(gtk.SELECTION_SINGLE)

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

class FolderTree( gtk.VBox ):
    store = [] # treeStore's (iterPath, filePath)
    openedFolders = [] # to make life easier when looking for folder...
    openedFiles = [] # to make life easier when looking for file...
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
            # newfile/folder appeared...
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
        cell.set_property("visible", True)
        cell.set_property("pixbuf", self.delete_pixbuf)

    def propertiesText(self, column, cell, liststore, iter):
        # value = liststore[iter]
        cell.props.weight = pango.WEIGHT_NORMAL

# treeview selection callbacks
    def onSelectListStore(self, path, listSelection):
        return True

    def onSelectTreeStore(self, path):
        # disable directories highlight.
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
        if filename:
            self.listStore.append([None, os.path.basename(filename)])

# opening/adding files
    def renderFolder(self, folder):
        def exclude(filename):
            for i in config.ignore:
                if re.search('\\'+i+'$', filename):
                    return False
            return True
        # do not open folder already open.
        if folder and folder in self.openedFolders:
            return
        self.openedFolders.append(folder)
        # triggers inotify monitoring
        self.monitor(folder)
        files = [f for f in os.listdir(folder)] # if f[0] <> '.'
        nextpath = []
        if files: # dir lvl 1
            for f in files:
                fpath = os.path.join(folder, f)
                if os.path.isdir(fpath):
                    self.monitor(fpath) # triggers inotify monitoring
                    self.openedFolders.append(fpath)
                    tpath = self.treeStore.append(None, [self.folder_pixbuf, f])
                    nextpath.append( (tpath, fpath) )
                    self.store.append( (tpath, fpath) )
                else:
                    if exclude(f):
                        tpath = self.treeStore.append(None, [self.file_pixbuf, f])
                        self.openedFiles.append(fpath)
                        self.store.append( (tpath, fpath) )
            while nextpath: # loop through remaining dir lvls
                dir = nextpath.pop(0)
                for f in os.listdir(dir[1]):
                    fpath = os.path.join(dir[1], f)
                    if os.path.isdir(fpath):
                        self.monitor(fpath) # triggers inotify monitoring
                        self.openedFolders.append(fpath)
                        tpath = self.treeStore.append(dir[0], [self.folder_pixbuf, f])
                        nextpath.append( (tpath, fpath) )
                        self.store.append( (tpath, fpath) )
                    else:
                        if exclude(f):
                            tpath = self.treeStore.append(dir[0], [self.file_pixbuf, f])
                            self.openedFiles.append(fpath)
                            self.store.append( (tpath, fpath) )

        print "opened folders:", self.openedFolders.__len__(),\
            "\n",\
            "opened files:", self.openedFiles.__len__(),\
            "\n",\
            "monitored folders:", self.monitoredFolders.__len__(),\
            "treestore entries:", self.store.__len__(),\
            self.openedFiles

    def clearTreeStore(self):
        self.treeStore.clear()
        self.store = [] # <<< WTF?
        self.openedFiles = []
        while self.openedFolders:
            dirmonitor = self.openedFolders.pop()
            self.disableDirMonitor(dirmonitor)
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
        if treeView.get_path_at_pos(int(event.x), int(event.y)):
            path = treeView.get_path_at_pos(int(event.x), int(event.y))[0]
        else:
            return
        selectedIter = self.treeStore.get_iter(path)
        filepath = self.reversePathFromIter(selectedIter)
        if event.button == 3 and os.path.isfile(filepath): # right clik on file
            self.contextMenu( [{'name':'build', 'activate':exit, 'path':path, 'event':event },
            {'name':'rename', 'activate':self.renameSelection, 'path':path, 'event':event },
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
    def makeHeadColumn(self, treeView):
        column = TreeViewColumn()
        # create a CellRenderers to render the data
        rendererpb = CellRendererPixbuf()
        rendererpb.set_property("visible", False)

        renderertxt = CellRendererText()
        renderertxt.props.mode = gtk.CELL_RENDERER_MODE_INERT
        #renderertxt.props.sensitive = False
        renderertxt.props.weight = pango.WEIGHT_BOLD
        # add the cells to the column
        column.pack_start( rendererpb, expand=False )
        column.pack_start( renderertxt, expand=False )

        column.set_attributes(renderertxt, text=1)

        treeView.selection.set_mode(gtk.SELECTION_NONE)

        treeView.append_column(column)

    def makeListColumn(self, treeView):
        column = TreeViewColumn()
        # create a CellRenderers to render the data
        rendererpb = CellRendererPixbuf()
        #rendererpb.set_property("follow-state", True)
        renderertxt = CellRendererText()
        # add the cells to the column
        column.pack_start( rendererpb, expand=False )
        column.pack_start( renderertxt, expand=False )
        column.set_attributes(renderertxt, text=1)
        column.set_cell_data_func(renderertxt, self.propertiesText)
        column.set_cell_data_func(rendererpb, self.propertiesIcon)

        treeView.selection.set_select_function(self.onSelectListStore, treeView.selection)

        treeView.append_column(column)

    def makeTreeColumn(self, treeView):
        rendererpb = CellRendererPixbuf()
        renderertxt = CellRendererText()
        
        column = gtk.TreeViewColumn()
        column.pack_start(rendererpb, expand=False)
        column.pack_start(renderertxt, expand=False)

        column.set_attributes(rendererpb, pixbuf=0)
        column.set_attributes(renderertxt, text=1)

        treeView.selection.set_select_function(self.onSelectTreeStore)
        treeView.selection.connect('changed', self.onTreeSelection)

        treeView.append_column(column)

    def __init__(self, gtkWindow):
        super( FolderTree, self ).__init__()
        self.current_directory = os.getcwd()
        self.Window = gtkWindow

        # listStore handles open files
        #self.listStore = ListStore()
        # treeStore handles folder trees
        self.treeStore = TreeStore()

        #self.headList = ListStore()
        self.headTree = ListStore()

        #treeViewHeadList = TreeView(self.headList)
        #self.headList.append([None, "OPENFILES"])

        # create the TreeView using ListStore
        #treeViewList = TreeView(self.listStore)
        #treeViewList.connect( "button-press-event", self.listMenu )
        
        treeViewHeadTree = TreeView(self.headTree)
        self.headTree.append([None, "FOLDERS"])

        # create the TreeView using TreeStore
        treeViewTree = TreeView(self.treeStore)
        treeViewTree.connect( "button-press-event", self.treeMenu )

        #self.TreeViewList.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        #self.TreeViewList.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#000000"))
        treeViewHeadTree.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        treeViewHeadTree.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#666666"))
        treeViewTree.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        treeViewTree.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#000000"))

        self.delete_pixbuf = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.normal_close )

        if config.icon_theme == False:
            self.file_pixbuf = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.file )
            self.folder_pixbuf = gtk.gdk.pixbuf_new_from_xpm_data( pixmap.folder )
        else:
            self.folder_pixbuf = self.TreeViewTree.render_icon(
                gtk.STOCK_DIRECTORY,
                gtk.ICON_SIZE_MENU, None)
            self.file_pixbuf = self.TreeViewTree.render_icon(
                gtk.STOCK_FILE,
                gtk.ICON_SIZE_MENU, None)

        #self.makeHeadColumn(treeViewHeadList)
        #self.makeListColumn(treeViewList)
        self.makeHeadColumn(treeViewHeadTree)
        self.makeTreeColumn(treeViewTree)

        #self.pack_start(treeViewHeadList, False)
        #self.pack_start(treeViewList, False)
        self.pack_start(treeViewHeadTree, False)
        self.pack_start(treeViewTree, True)
