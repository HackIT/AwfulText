import pygtk
pygtk.require('2.0')
import gtk, gobject, pango

leftxpm = [
    "11 13 3 1",
    ", c #ffffff",
    ". c #777776",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@.@@@",
    "@@@@@@...@@",
    "@@@@@....@@",
    "@@@@....@@@",
    "@@@@....@@@",
    "@@@@@....@@",
    "@@@@@@...@@",
    "@@@@@@@.@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

rightxpm = [
    "11 13 3 1",
    ", c #ffffff",
    ". c #777776",
    "@ c None",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@",
    "@@@.@@@@@@@",
    "@@...@@@@@@",
    "@@....@@@@@",
    "@@@....@@@@",
    "@@@....@@@@",
    "@@....@@@@@",
    "@@...@@@@@@",
    "@@@.@@@@@@@",
    "@@@@@@@@@@@",
    "@@@@@@@@@@@"
    ]

class Notebook( gtk.VBox ):
    def left(self, column, cell, liststore, iter):
        pbleft = gtk.gdk.pixbuf_new_from_xpm_data( leftxpm )
        cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        cell.set_property("visible", True)
        cell.set_property("pixbuf", pbleft)
        return False

    def right(self, column, cell, liststore, iter):
        pbright = gtk.gdk.pixbuf_new_from_xpm_data( rightxpm )
        cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        cell.set_property("visible", True)
        cell.set_property("pixbuf", pbright)
        return False

    def propertiesText(self, column, cell, liststore, iter):
        value = liststore[iter]
        # default cell layout style
        cell.props.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        cell.props.sensitive = False
        cell.props.weight = pango.WEIGHT_BOLD
        return False

    def onSelectListStore(self, path, listSelection):
        # disable highlight in liststore headers
        return False

    def __init__(self):
        super( Notebook, self ).__init__()
        liststore = gtk.ListStore(gobject.TYPE_STRING, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf)
        # create the TreeView using ListStore
        treeViewList = gtk.TreeView(liststore)
        #htest.TreeViewList.connect( "button-press-event", htest.listMenu )
        treeViewList.set_headers_visible(False)
        treeViewList.set_enable_search(False)
        treeViewList.unset_flags(gtk.CAN_FOCUS)
        # TODO openfiles
        liststore.append([" [ Untitled ] ", None, None])
        #htest.List.append([None, "somefile"])

        # create a CellRenderers to render the data
        cellRendererPixbufLeft = gtk.CellRendererPixbuf()
        cellRendererPixbufRight = gtk.CellRendererPixbuf()
        cellRendererTextList = gtk.CellRendererText()

        treeViewColumnList = gtk.TreeViewColumn()

        # add the cells to the columns - 2 in the first
        treeViewColumnList.pack_start( cellRendererTextList, False )
        treeViewColumnList.pack_start( cellRendererPixbufLeft, False )
        treeViewColumnList.pack_start( cellRendererPixbufRight, False )

        
        treeViewColumnList.set_attributes(cellRendererPixbufLeft, pixbuf=1)
        treeViewColumnList.set_attributes(cellRendererTextList, text=0)
        treeViewColumnList.set_attributes(cellRendererPixbufRight, pixbuf=2)

        treeViewColumnList.set_cell_data_func(cellRendererTextList, self.propertiesText)
        treeViewColumnList.set_cell_data_func(cellRendererPixbufLeft, self.left)
        treeViewColumnList.set_cell_data_func(cellRendererPixbufRight, self.right)

        treeViewList.append_column(treeViewColumnList)

        treeSelectionList = treeViewList.get_selection()
        #self.TreeSelection.connect( 'changed', self.callme )
        treeSelectionList.set_select_function(self.onSelectListStore, treeSelectionList)
        treeViewList.show_all()
        self.pack_start(treeViewList, False, False, 0)
