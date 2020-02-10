# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GLib as glib
from gi.repository import GdkPixbuf

# Python imports
import os, threading, time
from os.path import isdir, isfile, join
from os import listdir

# Application imports
from .Icon import Icon
from utils.FileHandler import FileHandler


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Grid:
    def __init__(self, grid, settings):
        self.grid            = grid
        self.settings        = settings
        self.fileHandler     = FileHandler(self.settings)

        self.store           = gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.usrHome         = settings.returnUserHome()
        self.hideHiddenFiles = settings.isHideHiddenFiles()
        self.builder         = settings.returnBuilder()
        self.ColumnSize      = settings.returnColumnSize()
        self.vidsFilter      = settings.returnVidsFilter()
        self.imagesFilter    = settings.returnImagesFilter()
        self.iconFactory     = Icon(settings)
        self.selectedFiles   = []
        self.currentPath     = ""

        self.grid.set_model(self.store)
        self.grid.set_pixbuf_column(0)
        self.grid.set_text_column(1)
        self.grid.connect("item-activated", self.iconDblLeftClick)
        self.grid.connect("button_release_event", self.iconSingleClick, (self.grid,))

    def setNewDirectory(self, path):
        self.store.clear()
        self.currentPath = path
        dirPaths         = ['.', '..']
        vids             = []
        images           = []
        desktop          = []
        files            = []

        for f in listdir(path):
            file = join(path, f)
            if self.hideHiddenFiles:
                if f.startswith('.'):
                    continue

            if isfile(file):
                lowerName = file.lower()

                if lowerName.endswith(self.vidsFilter):
                    vids.append(f)
                elif lowerName.endswith(self.imagesFilter):
                    images.append(f)
                elif lowerName.endswith((".desktop",)):
                    desktop.append(f)
                else:
                    files.append(f)
            else:
                dirPaths.append(f)

        dirPaths.sort()
        vids.sort()
        images.sort()
        desktop.sort()
        files.sort()

        files = dirPaths + vids + images + desktop + files
        self.generateGridIcons(path, files)
        self.fillVideoIcons(path, vids, len(dirPaths))


    @threaded
    def generateGridIcons(self, dirPath, files):
        for file in files:
            image = self.iconFactory.createIcon(dirPath, file).get_pixbuf()
            glib.idle_add(self.addToGrid, (image, file,))


    @threaded
    def fillVideoIcons(self, dirPath, files, start):
        model = self.grid.get_model()

        # Wait till we have a proper index...
        while len(self.store) < (start + 1):
            time.sleep(.200)

        i = start
        for file in files:
            self.updateGrid(model, dirPath, file, i)
            i += 1

    @threaded
    def updateGrid(self, model, dirPath, file, i):
        image = self.iconFactory.createThumbnail(dirPath, file).get_pixbuf()
        iter  = model.get_iter_from_string(str(i))
        glib.idle_add(self.replaceInGrid, (iter, image,))

    def addToGrid(self, dataSet):
        self.store.append([dataSet[0], dataSet[1]])

    def replaceInGrid(self, dataSet):
        # Iter, row column, new pixbuf...
        self.store.set_value(dataSet[0], 0 , dataSet[1])


    def iconDblLeftClick(self, widget, item):
        try:
            model    = widget.get_model()
            fileName = model[item][1]
            dir      = self.currentPath
            file     = dir + "/" + fileName

            if fileName == ".":
                self.setNewDirectory(dir)
            elif fileName == "..":
                parentDir        = os.path.abspath(os.path.join(dir, os.pardir))
                self.currentPath = parentDir
                self.setNewDirectory(parentDir)
                self.settings.saveSettings(parentDir)
            elif isdir(file):
                self.currentPath = file
                self.setNewDirectory(self.currentPath)
                self.settings.saveSettings(self.currentPath)
            elif isfile(file):
                self.fileHandler.openFile(file)
        except Exception as e:
            print(e)

    def iconSingleClick(self, widget, eve, rclicked_icon):
        try:
            if eve.type == gdk.EventType.BUTTON_RELEASE and eve.button == 1:
                self.selectedFiles.clear()
                items    = widget.get_selected_items()
                model    = widget.get_model()
                dir      = self.currentPath

                for item in items:
                    fileName = model[item][1]

                    if fileName != "." and fileName != "..":
                        file = dir + "/" + fileName
                        self.selectedFiles.append(file) # Used for return to caller

            elif eve.type == gdk.EventType.BUTTON_RELEASE and eve.button == 3:
                input          = self.builder.get_object("filenameInput")
                controls       = self.builder.get_object("iconControlsWindow")
                iconsButtonBox = self.builder.get_object("iconsButtonBox")
                menuButtonBox  = self.builder.get_object("menuButtonBox")


                if len(self.selectedFiles) == 1:
                    parts = self.selectedFiles[0].split("/")
                    input.set_text(parts[len(parts) - 1])
                    input.show()
                    iconsButtonBox.show()
                    menuButtonBox.hide()
                    controls.show()
                elif len(self.selectedFiles) > 1:
                    input.set_text("")
                    input.hide()
                    menuButtonBox.hide()
                    iconsButtonBox.show()
                    controls.show()
                else:
                    input.set_text("")
                    input.show()
                    menuButtonBox.show()
                    iconsButtonBox.hide()
                    controls.show()

        except Exception as e:
            print(e)

    def returnSelectedFiles(self):
        # NOTE: Just returning selectedFiles looks like it returns a "pointer"
        # to the children. This means we lose the list if any left click occures
        # in this class.
        files = []
        for file in self.selectedFiles:
            files.append(file)
        return files

    def returnCurrentPath(self):
        currentPath = self.currentPath
        return currentPath
