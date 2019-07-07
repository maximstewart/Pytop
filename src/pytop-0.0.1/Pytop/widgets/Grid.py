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
        self.grid          = grid
        self.settings      = settings
        self.fileHandler   = FileHandler(self.settings)

        self.store         = gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.usrHome       = settings.returnUserHome()
        self.builder       = settings.returnBuilder()
        self.ColumnSize    = settings.returnColumnSize()
        self.vidsFilter    = settings.returnVidsFilter()
        self.imagesFilter  = settings.returnImagesFilter()
        self.iconFactory   = Icon(settings)
        self.gtkLock       = False  # Thread checks for gtkLock
        self.threadLock    = False  # Gtk checks for thread lock
        self.helperThread  = None   # Helper thread object
        self.toWorkPool    = []     # Thread fills pool and gtk empties it
        self.selectedFiles = []
        self.currentPath   = ""

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
            if self.settings.isHideHiddenFiles():
                if f.startswith('.'):
                    continue
            if isfile(file):
                if file.lower().endswith(self.vidsFilter):
                    vids.append(f)
                elif file.lower().endswith(self.imagesFilter):
                    images.append(f)
                elif file.lower().endswith((".desktop",)):
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

        if self.helperThread:
            self.helperThread.terminate()
            self.helperThread = None

        # Run helper thread...
        self.threadLock   = True
        self.helperThread = threading.Thread(target=self.generateGridIcon, args=(path, files)).start()
        glib.idle_add(self.addToGrid, (file,))  # NOTE: This must stay in the main thread b/c
                                                # gtk isn't thread safe/aware So, we
                                                # make a sad lil thread hot potato 'game'
                                                # out of this process.


    # @threaded
    def generateGridIcon(self, dirPath, files):
        # NOTE: We'll be passing pixbuf after retreval to keep Icon.py file more
        # universaly usable. We can just remove get_pixbuf to get a gtk.Image type
        for file in files:
            image = self.iconFactory.createIcon(dirPath, file)
            self.toWorkPool.append([image.get_pixbuf(), file])
            self.threadLock = False
            self.gtkLock    = True


    def addToGrid(self, args):
        # NOTE: Returning true tells gtk to check again in the future when idle.
        # False ends checks and "continues normal flow"
        files = args[0]

        if len(self.toWorkPool) > 0:
            for dataSet in self.toWorkPool:
                self.store.append(dataSet)

        if len(self.store) == len(files): # Confirm processed all files and cleanup
            self.gtkLock    = False
            self.threadLock = False
            self.toWorkPool.clear()
            return False
            # Check again when idle; If nothing else is updating, this function
            # gets called immediatly. So, we play hot potato by setting lock to Thread
        else:
            self.toWorkPool.clear()
            self.gtkLock    = False
            self.threadLock = True
            time.sleep(.005) # Fixes refresh and up icon not being added.
            return True

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
            elif isdir(file):
                self.currentPath = file
                self.setNewDirectory(self.currentPath)
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
        # to the children. This mean we lose the list if any left click occures
        # in this class.
        files = []
        for file in self.selectedFiles:
            files.append(file)
        return files

    def returnCurrentPath(self):
        return self.currentPath
