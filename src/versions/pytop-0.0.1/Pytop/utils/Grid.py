

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject as gobject

# Python imports
import os, threading
from os.path import isdir, isfile, join
from os import listdir
from .Icon import Icon
from .FileHandler import FileHandler


gdk.threads_init()

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Grid:
    def __init__(self, desktop, settings, newPath):
        self.desktop      = desktop
        self.settings     = settings
        self.filehandler  = FileHandler()

        self.store        =  gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.usrHome      = settings.returnUserHome()
        self.builder      = self.settings.returnBuilder()
        self.ColumnSize   = self.settings.returnColumnSize()
        self.currentPath  = ""
        self.selectedFile = ""

        self.desktop.set_model(self.store)
        self.desktop.set_pixbuf_column(0)
        self.desktop.set_text_column(1)
        self.desktop.connect("item-activated", self.iconLeftClickEventManager)
        self.desktop.connect("button_press_event", self.iconRightClickEventManager, (self.desktop,))

        self.setIconViewDir(newPath)

    @threaded
    def setIconViewDir(self, path):
        self.store.clear()

        self.currentPath = path
        dirPaths         = ['.', '..']
        files            = []

        for f in listdir(path):
            file = join(path, f)
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue
            if isfile(file):
                files.append(f)
            else:
                dirPaths.append(f)

        dirPaths.sort()
        files.sort()
        files = dirPaths + files
        self.generateDirectoryGrid(path, files)

    def generateDirectoryGrid(self, dirPath, files):
        fractionTick = 1.0 / 1.0 if len(files) == 0 else len(files)
        tickCount    = 0.0
        row          = 0
        col          = 0
        x            = 0
        y            = 0

        loadProgress = self.builder.get_object('loadProgress')
        loadProgress.set_text("Loading...")
        loadProgress.set_fraction(0.0)

        for file in files:
            imgBuffer = Icon(self.settings).createIcon(dirPath, file)
            gobject.idle_add(self.addToGrid, (imgBuffer, file,))
            tickCount += fractionTick
            loadProgress.set_fraction(tickCount)

        loadProgress.set_text("Finished...")

    def addToGrid(self, args):
        self.store.append([args[0], args[1]])

    def iconLeftClickEventManager(self, widget, item):
        try:
            model    = widget.get_model()
            fileName = model[item][1]
            dir      = self.currentPath
            file     = dir + "/" + fileName

            if fileName == ".":
                self.setIconViewDir(dir)
            elif fileName == "..":
                parentDir        = os.path.abspath(os.path.join(dir, os.pardir))
                self.currentPath = parentDir
                self.setIconViewDir(parentDir)
            elif isdir(file):
                self.currentPath = file
                self.setIconViewDir(self.currentPath)
            elif isfile(file):
                self.filehandler.openFile(file)
        except Exception as e:
            print(e)

    def iconRightClickEventManager(self, widget, eve, params):
        try:
            if eve.type == gdk.EventType.BUTTON_PRESS and eve.button == 3:
                # # NOTE: Need to change name of listview box...
                # children = widget.get_children()[0].get_children()
                # fileName = children[1].get_text()
                # dir      = self.currentPath
                # file     = dir + "/" + fileName
                #
                # input    = self.builder.get_object("iconRenameInput")
                popover  = self.builder.get_object("iconControlsWindow")
                # self.selectedFile = file # Used for return to caller
                #
                # input.set_text(fileName)
                popover.set_relative_to(widget)
                popover.set_position(gtk.PositionType.RIGHT)
                popover.show_all()
                popover.popup()
        except Exception as e:
            print(e)


    # Passthrough file control events
    def createFile(arg):
        pass

    def updateFile(self, file):
        newName = self.currentPath + "/" + file
        status  = self.filehandler.updateFile(self.selectedFile, newName)

        if status == 0:
            self.selectedFile = newName
            self.generateDirectoryGrid(self.currentPath)

    def deleteFile(self):
        status = self.filehandler.deleteFile(self.selectedFile)

        if status == 0:
            self.selectedFile = ""
            self.generateDirectoryGrid(self.currentPath)

    def copyFile(self):
        pass

    def cutFile(self):
        pass

    def pasteFile(self):
        pass
