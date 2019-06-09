

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GObject as gobject


# Python imports
from .Icon import Icon
from .FileHandler import FileHandler
import os, subprocess
from os.path import isdir, isfile, join
from os import listdir


class Grid:
    def __init__(self, desktop, settings):
        self.desktop     = desktop
        self.settings    = settings
        self.filehandler = FileHandler()

        self.currentPath = ""
        self.builder     = self.settings.returnBuilder()
        self.ColumnSize  = self.settings.returnColumnSize()


    def generateDirectoryGrid(self, dirPath):
        dirPaths      = ['.', '..']
        files         = []

        # self.desktop.connect("button_press_event", self.showGridControlMenu, ())

        for f in listdir(dirPath):
            file = join(dirPath, f)
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue

            if isfile(file):
                files.append(f)
            else:
                dirPaths.append(f)

        dirPaths.sort()
        files.sort()

        files        = dirPaths + files
        fractionTick = 1.0 / 1.0 if len(files) == 0 else len(files)
        tickCount    = 0.0
        row          = 0
        col          = 0
        x            = 0
        y            = 0

        loadProgress = self.builder.get_object('loadProgress')
        loadProgress.set_text("Loading...")
        loadProgress.set_fraction(0.0)
        self.clearGrid(self.desktop)
        for file in files:
            eveBox = Icon().createIcon(dirPath, file)
            # self.drag.connectEvents(self.desktop, eveBox)
            eveBox.connect("button_press_event", self.iconClickEventManager, (eveBox,))
            eveBox.connect("enter_notify_event", self.settings.mouseOver, ())
            eveBox.connect("leave_notify_event", self.settings.mouseOut, ())

            gobject.idle_add(self.addToGrid, (self.desktop, eveBox, col, row,))
            tickCount = tickCount + fractionTick
            loadProgress.set_fraction(tickCount)

            col += 1
            if col == self.ColumnSize:
                col = 0
                row += 1

        self.desktop.show_all()
        loadProgress.set_text("Finished...")

    def addToGrid(self, args):
        args[0].attach(args[1], args[2], args[3], 1, 1)

    def clearGrid(self, object):
        while True:
            if object.get_child_at(0,0)!= None:
                object.remove_row(0)
            else:
                break

    def iconClickEventManager(self, widget, eve, params):
        self.settings.setSelected(params[0])
        if eve.type == gdk.EventType.DOUBLE_BUTTON_PRESS:
            children = widget.get_children()[0].get_children()
            fileName = children[1].get_text()
            dir      = self.currentPath
            file     = dir + "/" + fileName

            if fileName == ".":
                self.generateDirectoryGrid(dir)
            elif fileName == "..":
                parentDir        = os.path.abspath(os.path.join(dir, os.pardir))
                self.currentPath = parentDir
                self.generateDirectoryGrid(parentDir)
            elif isdir(file):
                self.currentPath = file
                Thread(target=self.generateDirectoryGrid, args=(self.currentPath,)).start()
            else:
                self.filehandler.openFile(file)
        elif eve.type == gdk.EventType.BUTTON_PRESS and eve.button == 3:
            children = widget.get_children()[0].get_children()
            input    = self.builder.get_object("iconRenameInput")
            popover  = self.builder.get_object("iconControlsWindow")

            input.set_text(children[1].get_text())
            popover.set_relative_to(children[1])
            popover.set_position(gtk.PositionType.RIGHT)
            popover.show_all()
            popover.popup()
