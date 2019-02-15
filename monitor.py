#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, gio, glib

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

class Inotify(gio.File):
    store = [] # treeStore's (iterPath, filePath)
    openedFolders = [] # to make life easier when looking for file...
    openedFiles = []
    monitoredFolders = [] # glib's monitoring storage... doesn't work without storing it.
    file_monitor_changed_type = None

    def dbg(self, *vars):
        print vars

    def __init__(self, dir):
        super( Monitor, self ).__init__(dir)
        mdir = self.monitor_directory()
        mdir.set_rate_limit(0)
        mdir.set_data("path", mdir)
        mdir.connect("changed", self.monitorEvent)

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
