#!/usr/bin/python3

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GObject as gobject
from gi.repository import WebKit2 as webkit


# Python imports
import os, threading, subprocess, hashlib
from utils import Settings, Icon, FileHandler, Dragging
from os.path import isdir, isfile, join
from threading import Thread
from os import listdir


gdk.threads_init()


class Main:
    def __init__(self):
        # Needed for glade file load to work right...
        webkit.WebView()

        self.builder     = gtk.Builder()
        self.filehandler = FileHandler()
        self.settings    = Settings()
        # self.drag        = Dragging()
        self.settings.attachBuilder(self.builder)
        self.builder.connect_signals(self)

        self.currentPath     = ""
        window               = self.settings.createWindow()
        self.usrHome         = self.settings.returnUserHome()
        self.desktopPath     = self.settings.returnDesktopPath()
        self.ColumnSize      = self.settings.returnColumnSize()
        self.desktop         = self.builder.get_object("Desktop")

        # Add filter to allow only folders to be selected
        self.loadProgress = self.builder.get_object("loadProgress")
        selectedDirDialog = self.builder.get_object("selectedDirDialog")
        filefilter        = self.builder.get_object("Folders")
        selectedDirDialog.add_filter(filefilter)
        selectedDirDialog.set_filename(self.desktopPath)
        self.setDir(selectedDirDialog)

        self.webview = self.builder.get_object("webview")
        self.settings.setDefaultWebviewSettings(self.webview, self.webview.get_settings())
        self.webview.load_uri(self.settings.returnWebHome())

        window.fullscreen()
        window.show_all()


    def setDir(self, widget, data=None):
        self.currentPath = widget.get_filename()
        self.getDirectoryList(self.currentPath)
        # Thread(target=self.getDirectoryList, args=(self.currentPath,)).start()

    def getDirectoryList(self, dir):
        dirs   = ['.', '..']
        files  = []

        for f in listdir(dir):
            file = join(dir, f)
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue

            if isfile(file):
                files.append(f)
            else:
                dirs.append(f)

        dirs.sort()
        files.sort()

        files        = dirs + files
        fractionTick = 1.0 / 1.0 if len(files) == 0 else len(files)
        tickCount    = 0.0
        row          = 0
        col          = 0
        x            = 0
        y            = 0

        self.loadProgress.set_text("Loading...")
        self.loadProgress.set_fraction(0.0)
        self.clear(self.desktop)
        for file in files:
            eveBox = Icon().createIcon(dir, file)
            # self.drag.connectEvents(self.desktop, eveBox)
            eveBox.connect("button_press_event", self.clickManager, (eveBox,))
            eveBox.connect("enter_notify_event", self.settings.mouseOver, ())
            eveBox.connect("leave_notify_event", self.settings.mouseOut, ())

            gobject.idle_add(self.addToGrid, (self.desktop, eveBox, col, row,))
            tickCount = tickCount + fractionTick
            self.loadProgress.set_fraction(tickCount)

            col += 1
            if col == self.ColumnSize:
                col = 0
                row += 1

        self.desktop.show_all()
        self.loadProgress.set_text("Finished...")

    def addToGrid(self, args):
        args[0].attach(args[1], args[2], args[3], 1, 1)

    def clickManager(self, widget, eve, params):
        self.settings.setSelected(params[0])
        if eve.type == gdk.EventType.DOUBLE_BUTTON_PRESS:
            box      = widget.get_children()[0]
            children = box.get_children()
            fileName = children[1].get_text()
            dir      = self.currentPath
            file     = dir + "/" + fileName

            if fileName == ".":
                self.getDirectoryList(dir)
            elif fileName == "..":
                parentDir        = os.path.abspath(os.path.join(dir, os.pardir))
                self.currentPath = parentDir
                self.getDirectoryList(parentDir)
            elif isdir(file):
                self.currentPath = file
                self.getDirectoryList(file)
                # Thread(target=self.getDirectoryList, args=(file,)).start()
            else:
                self.filehandler.openFile(file)
        elif eve.type == gdk.EventType.BUTTON_PRESS and eve.button == 3:
            box      = widget.get_children()[0]
            children = box.get_children()

            popover = self.builder.get_object("controlsWindow")
            popover.set_relative_to(children[1])
            popover.set_position(gtk.PositionType.RIGHT)
            popover.show_all()

            input = self.builder.get_object("renamerInput")
            input.set_text(children[1].get_text())

            popover.popup()



    def showWebview(self, widget):
        self.builder.get_object("webViewer").popup()

    def loadHome(self, widget):
        self.webview.load_uri(self.settings.returnWebHome())

    def runSearchWebview(self, widget, data=None):
        if data.keyval == 65293:
            self.webview.load_uri(widget.get_text().strip())

    def refreshPage(self, widget, data=None):
        self.webview.load_uri(self.webview.get_uri())

    def setUrlBar(self, widget, data=None):
        self.builder.get_object("webviewSearch").set_text(widget.get_uri())


    def clear(self, object):
        while True:
            if object.get_child_at(0,0)!= None:
                object.remove_row(0)
            else:
                break


if __name__ == "__main__":
    main = Main()
    gtk.main()
