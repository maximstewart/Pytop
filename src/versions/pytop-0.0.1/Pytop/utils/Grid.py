

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GObject as gobject

# Python imports
import os, subprocess, threading, hashlib
from os.path import isdir, isfile, join
from os import listdir
from threading import Thread
from .Icon import Icon
from .FileHandler import FileHandler


gdk.threads_init()
class Grid:
    def __init__(self, desktop, settings):
        self.desktop     = desktop
        self.settings    = settings
        self.filehandler = FileHandler()

        self.usrHome     = settings.returnUserHome()
        self.builder     = self.settings.returnBuilder()
        self.ColumnSize  = self.settings.returnColumnSize()
        self.thubnailGen = self.settings.getThumbnailGenerator()

        self.currentPath  = ""
        self.selectedFile = ""


    def generateDirectoryGrid(self, dirPath):
        loadProgress = self.builder.get_object('loadProgress')
        loadProgress.set_text("Loading...")
        loadProgress.set_fraction(0.0)
        self.clearGrid(self.desktop)
        self.currentPath = dirPath
        dirPaths         = ['.', '..']
        files            = []

        for f in listdir(dirPath):
            file = join(dirPath, f)
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue
            if isfile(file):
                files.append(f)
            else:
                dirPaths.append(f)

        vidsList     = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        fractionTick = 1.0 / 1.0 if len(files) == 0 else len(files)
        tickCount    = 0.0
        row          = 0
        col          = 0
        x            = 0
        y            = 0

        dirPaths.sort()
        files.sort()
        files    = dirPaths + files
        for file in files:
            eveBox = gtk.EventBox()

            # Generate any thumbnails beforehand...
            if file.lower().endswith(vidsList):
                fullPathFile = dirPath + "/" + file
                fileHash     = hashlib.sha256(str.encode(fullPathFile)).hexdigest()
                hashImgpth   = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"
                if isfile(hashImgpth) == False:
                    self.generateVideoThumbnail(fullPathFile, hashImgpth)
                eveBox = self.generateIcon(dirPath, file, col, row)
            else:
                eveBox = self.generateIcon(dirPath, file, col, row)

            eveBox.show_all()
            gobject.idle_add(self.addToGrid, (self.desktop, eveBox, col, row,))
            tickCount = tickCount + fractionTick
            loadProgress.set_fraction(tickCount)

            col += 1
            if col == self.ColumnSize:
                col = 0
                row += 1

        loadProgress.set_text("Finished...")

    def generateIcon(self, dirPath, file, col, row):
        eveBox = Icon(self.settings).createIcon(dirPath, file)
        # self.drag.connectEvents(self.desktop, eveBox)
        eveBox.connect("button_press_event", self.iconClickEventManager, (eveBox,))
        eveBox.connect("enter_notify_event", self.settings.mouseOver, ())
        eveBox.connect("leave_notify_event", self.settings.mouseOut, ())
        return eveBox


    def addToGrid(self, args):
        args[0].attach(args[1], args[2], args[3], 1, 1)

    def clearGrid(self, object):
        while True:
            if object.get_child_at(0,0)!= None:
                object.remove_row(0)
            else:
                break

    def iconClickEventManager(self, widget, eve, params):
        try:
            self.settings.setSelected(params[0])
            children = widget.get_children()[0].get_children()
            fileName = children[1].get_text()
            dir      = self.currentPath
            file     = dir + "/" + fileName

            if eve.type == gdk.EventType.DOUBLE_BUTTON_PRESS:
                if fileName == ".":
                    self.setNewPath(dir)
                elif fileName == "..":
                    parentDir        = os.path.abspath(os.path.join(dir, os.pardir))
                    self.currentPath = parentDir
                    self.setNewPath(parentDir)
                elif isdir(file):
                    self.currentPath = file
                    self.setNewPath(self.currentPath)
                elif isfile(file):
                    self.filehandler.openFile(file)
            elif eve.type == gdk.EventType.BUTTON_PRESS and eve.button == 3:
                input    = self.builder.get_object("iconRenameInput")
                popover  = self.builder.get_object("iconControlsWindow")
                self.selectedFile = file # Used for return to caller

                input.set_text(fileName)
                popover.set_relative_to(children[1])
                popover.set_position(gtk.PositionType.RIGHT)
                popover.show_all()
                popover.popup()
        except Exception as e:
            print(e)

    def generateVideoThumbnail(self, fullPathFile, hashImgpth):
        subprocess.call([self.thubnailGen, "-t", "65%", "-s", "300", "-c", "jpg", "-i", fullPathFile, "-o", hashImgpth])

    def setNewPath(self, path):
        self.generateDirectoryGrid(path)
        # NOTE: Threading here causes seg faults. My theory is that
        # the calling threading dies b/c the grid itself is cleard
        # of children and the child is the one that has the 'thread'
        #
        # Thread(target=self.generateDirectoryGrid, args=(path,)).start()


    # Pass through file control events
    def renameFile(self, file):
        newName = self.currentPath + "/" + file
        status  = self.filehandler.renameFile(self.selectedFile, newName)

        if status == 0:
            self.selectedFile = newName
            self.generateDirectoryGrid(self.currentPath)


    def deleteFile(self):
        status = self.filehandler.deleteFile(self.selectedFile)

        if status == 0:
            self.selectedFile = ""
            self.generateDirectoryGrid(self.currentPath)
