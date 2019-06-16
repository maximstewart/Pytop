

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib

# Python imports
import os, threading
from os.path import isdir, isfile, join
from os import listdir
from .Icon import Icon
from .FileHandler import FileHandler


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Grid:
    def __init__(self, desktop, settings, newPath):
        self.desktop      = desktop
        self.settings     = settings
        self.filehandler  = FileHandler()

        self.store        = gtk.TreeStore(str, GdkPixbuf.Pixbuf)
        self.usrHome      = settings.returnUserHome()
        self.builder      = self.settings.returnBuilder()
        self.ColumnSize   = self.settings.returnColumnSize()
        self.currentPath  = ""
        self.selectedFile = ""
        self.treeViewCol  = None
        self.desktop.set_model(self.store)

        if len(self.desktop.get_columns()) == 0:
            self.treeViewCol  = gtk.TreeViewColumn("Files")
            # Create a column cell to display text
            colCellText = gtk.CellRendererText()
            # Create a column cell to display an image
            colCellImg = gtk.CellRendererPixbuf()
            # Add the cells to the column
            self.treeViewCol.pack_start(colCellImg, False)
            self.treeViewCol.pack_start(colCellText, True)
            # Bind the text cell to column 0 of the tree's model
            self.treeViewCol.add_attribute(colCellText, "text", 0)
            # Bind the image cell to column 1 of the tree's model
            self.treeViewCol.add_attribute(colCellImg, "pixbuf", 1)
            # Append the columns to the TreeView
            self.desktop.append_column(self.treeViewCol)
        else:
            self.treeViewCol = self.desktop.get_column(0)

        self.setIconViewDir(newPath)


    def setIconViewDir(self, path):
        # self.treeViewCol.clear()
        self.store.clear()

        self.currentPath = path
        paths            = ['.', '..']
        files            = []

        for f in listdir(path):
            file = join(path, f)
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue
            if isfile(file):
                files.append(f)
            else:
                paths.append(f)

        paths.sort()
        files.sort()
        files = paths + files
        self.generateDirectoryGrid(path, files)

    @threaded
    def generateDirectoryGrid(self, path, files):
        fractionTick = 1.0 / 1.0 if len(files) == 0 else len(files)
        tickCount    = 0.0

        loadProgress = self.builder.get_object('loadProgress')
        loadProgress.set_text("Loading...")
        loadProgress.set_fraction(0.0)
        for file in files:
            imgBuffer = self.getImgBuffer(path, file)
            GLib.idle_add(self.addToGrid, (imgBuffer, file,))
            # tickCount += fractionTick
            loadProgress.set_fraction(tickCount)
        loadProgress.set_text("Finished...")

    def getImgBuffer(self, path, file):
        return Icon(self.settings).createIcon(path, file)

    def addToGrid(self, args, parent=None):
        # NOTE: Converting to pixbuf after retreval to keep Icon.py more universal.
        # We can just remove get_pixbuf to get a gtk image.
        # We probably need a settings check to chose a set type...
        self.store.append(parent, [args[1], args[0].get_pixbuf()])


    def iconLeftClickEventManager(self, widget, eve, item):
        tree_selection    = self.desktop.get_selection()
        (model, pathlist) = tree_selection.get_selected_rows()
        fileName          = None
        dir               = self.currentPath
        for path in pathlist :
            tree_iter = model.get_iter(path)
            fileName = model.get_value(tree_iter,0)

        try:
            file = dir + "/" + fileName

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


    def returnParentDir(self):
        return os.path.abspath(os.path.join(self.currentPath, os.pardir))

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
