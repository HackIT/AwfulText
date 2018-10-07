#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, os, stat, gobject, pango, re
from dialog import OpenFolderDialog

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
delete_icon = gtk.gdk.pixbuf_new_from_xpm_data( crossxpm )

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
folderpb = gtk.gdk.pixbuf_new_from_xpm_data( folderxpm )

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
filepb = gtk.gdk.pixbuf_new_from_xpm_data( filexpm )

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

class fugg( gtk.VBox ):
    def __init__(self):
        super( fugg, self ).__init__()

class FileBrowser( gtk.VBox ):
    headers = [(0,)]
    openedFolders = []
    def icon(self, column, cell, liststore, iter):
        cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        cell.props.sensitive = True
        # for cells that acts as hearders
        for head in self.headers:
            if liststore.get_path(iter) == head:
                cell.set_property("visible", False)
                return
        cell.set_property("visible", True)
        cell.set_property("pixbuf", delete_icon)
    
    #def fsicon(self, column, cell, treestore, iter):
    #    cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
    #    cell.props.sensitive = True
    #    
    #    # for cells that acts as hearders
    #    #for head in self.headers:
    #    #    if treestore.get_path(iter) == head:
    #    #        cell.set_property("visible", False)
    #    #        return
    #    dname = os.path.expanduser('~')
    #    #print dname, treestore.get_value(iter, 1)
    #    filename = os.path.join(dname, treestore.get_value(iter, 1))
    #    filestat = os.stat(filename)
    #    if stat.S_ISDIR(filestat.st_mode):
    #        pb = folderpb
    #    else:
    #         pb = filepb
    #    cell.set_property("pixbuf", pb)
    #    cell.set_property("visible", True)

    def makelist(self, column, cell, liststore, iter):
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
                # cell.props.xalign = 0.0
            #print cell.props.text

        #print cell.get_properties("attributes")
        #cell.props.text = value.name
        #print value
        #if value.description is None:print cell.get_properties("attributes")

        #else:
        #    cell.props.weight = pango.WEIGHT_NORMAL
    
    def onSelectListStore(self, path, listSelection):
        print 'called', path
        # print type(listSelection.get_selected())
        # print treeModel.get_value(treeIter, 0)
        for head in self.headers:
            if path == head:
                return False
        return True

    def onSelectTreeStore(self, path, treeSelection):
        if not self.Tree.iter_has_child(self.Tree.get_iter(path)):
            liter = self.Tree.get_iter(path)
            #while self.Tree.iter_parent(liter)
            rootIter = self.Tree.get_iter_first()
            print self.Tree.get_value(rootIter, 1)
            #re.search()
            print 'called', self.Tree.get_value(self.Tree.get_iter(path), 1), len(self.Tree)
        # print treeModel.get_value(treeIter, 0)

    def renderFolder(self, folder):
        if folder:
            if len(self.headers) < 2:
                self.headers.append( self.List.get_path( self.List.append([None, 'FOLDERS']) ) )
            self.openedFolders.append(folder)
            files = [f for f in os.listdir(folder) if f[0] <> '.']
            for f in files:
                if os.path.isdir(os.path.join(folder, f)):
                    pdir = self.Tree.append(None, [folderpb,f])
                    for s in os.listdir(folder+"/"+f):
                        if not s[0] == '.':
                            if os.path.isdir(os.path.join(folder+"/"+f, s)):
                                continue
                            else:
                                self.Tree.append(pdir, [filepb,s])
                else:
                    self.Tree.append(None,[filepb, f])

    def addFolder(self, ImageMenuItem):
        dialog = OpenFolderDialog()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.renderFolder(dialog.get_filename())
        dialog.destroy()

    def openFolder(self, ImageMenuItem):
        dialog = OpenFolderDialog()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.Tree.clear()
            self.renderFolder(dialog.get_filename())
        dialog.destroy()
                # manager = self.get_data('languages-manager')
                # if os.path.isabs(filename):
                #     path = filename
                # else:
                #     path = os.path.abspath(filename)
                # language = manager.guess_language(filename)
                # self.begin_not_undoable_action()
                # try:
                #     txt = open(path).read()
                # except:
                #     return False
                
            #if language:
            #    self.set_highlight_syntax(True)
            #    self.set_language(language)
            #else:
            #    print 'No language found for file "%s"' % filename
            #    self.set_highlight_syntax(False)
            #self.set_text(txt)
            #self.set_data('filename', path)
            #self.end_not_undoable_action()
            #self.set_modified(False)
            #self.place_cursor(self.get_start_iter())

    def __init__(self):
        super( FileBrowser, self ).__init__()
        self.current_directory = os.getcwd()
        # create liststore
        self.List = ListStore()
        self.Tree = TreeStore()
        # create the TreeView using ListStore
        
        self.TreeViewList = gtk.TreeView(self.List)
        self.TreeViewList.set_headers_visible(False)

        self.TreeViewTree = gtk.TreeView(self.Tree)
        self.TreeViewTree.set_headers_visible(False)
        treeselect = self.TreeViewTree.get_selection()
        treeselect.set_mode( gtk.SELECTION_SINGLE)
        #self.TreeViewList.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        #self.TreeViewList.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#000000"))
        #self.TreeViewTree.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color("#bbbbbb"))
        #self.TreeViewTree.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#000000"))

        self.List.append([None, "OPENFILES"])
        self.List.append([None, "somefile"])

        # create a CellRenderers to render the data
        self.CellRendererPixbufList = CellRendererPixbuf()
        self.CellRendererTextList = CellRendererText()
        self.CellRendererTextTree = CellRendererText()
        self.CellRendererPixbufTree = CellRendererPixbuf()

        self.TreeViewColumnList = TreeViewColumn()

        # add the cells to the columns - 2 in the first
        self.TreeViewColumnList.pack_start( self.CellRendererPixbufList, False )
        self.TreeViewColumnList.pack_start( self.CellRendererTextList, False )
        self.TreeViewColumnList.set_cell_data_func(self.CellRendererPixbufList, self.icon)
        #self.TreeViewColumnList.set_attributes(self.CellRendererPixbufList, stock_id=0)
        self.TreeViewColumnList.set_attributes(self.CellRendererTextList, text=1)
        self.TreeViewColumnList.set_cell_data_func(self.CellRendererTextList, self.makelist)

        self.TreeViewList.append_column(self.TreeViewColumnList)

        self.TreeViewColumnTree = gtk.TreeViewColumn()
        self.TreeViewColumnTree.pack_start( self.CellRendererPixbufTree, False)
        self.TreeViewColumnTree.pack_start(self.CellRendererTextTree, False)
        #self.TreeViewColumnTree.set_cell_data_func(self.CellRendererPixbufTree, self.fsicon)
        self.TreeViewColumnTree.set_attributes(self.CellRendererPixbufTree, pixbuf=0)
        self.TreeViewColumnTree.set_attributes(self.CellRendererTextTree, text=1)
        #self.TreeViewColumnTree.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        #self.TreeViewColumnTree.set_cell_data_func(self.CellRendererPixbufTree, self.fsicon)
        # add columns to treeview
        self.TreeViewTree.append_column(self.TreeViewColumnTree)

        self.TreeSelectionList = self.TreeViewList.get_selection()
        #self.TreeSelection.connect( 'changed', self.callme )
        self.TreeSelectionList.set_select_function(self.onSelectListStore, self.TreeSelectionList)
        
        self.TreeSelectionTree = self.TreeViewTree.get_selection()
        #self.TreeSelection.connect( 'changed', self.callme )
        self.TreeSelectionTree.set_select_function(self.onSelectTreeStore, self.TreeSelectionTree)

        self.pack_start(self.TreeViewList, False)
        self.pack_start(self.TreeViewTree, False)

    def aye(self, treeSelection):
        print "called", treeSelection
        treeModel, treeIter = treeSelection.get_selected()
        print treeModel.get_value(treeIter, 0)
