# Python imports
import os, threading, time
from os.path import isdir, isfile, join
from os import listdir


# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GdkPixbuf


# Application imports
from .icon import Icon
from utils.file_handler import FileHandler


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Grid:
    def __init__(self, _grid, _settings):
        self.grid            = _grid
        self.settings        = _settings
        self.fileHandler     = FileHandler(self.settings)

        self.store           = Gtk.ListStore(GdkPixbuf.Pixbuf or None, str)
        self.usrHome         = self.settings.get_user_home()
        self.hideHiddenFiles = self.settings.isHideHiddenFiles()
        self.builder         = self.settings.get_builder()
        self.ColumnSize      = self.settings.getColumnSize()
        self.vidsFilter      = self.settings.getVidsFilter()
        self.imagesFilter    = self.settings.getImagesFilter()
        self.iconFactory     = Icon(self.settings)
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


    def generateGridIcons(self, dir, files):
        for i, file in enumerate(files):
            self.store.append([None, file])
            self.create_icon(i, dir, file)


    @threaded
    def create_icon(self, i, dir, file):
        icon  = self.iconFactory.create_icon(dir, file)
        fpath = f"{dir}/{file}"
        GLib.idle_add(self.update_store, (i, icon, fpath,))

    def update_store(self, item):
        i, icon, fpath = item
        itr  = self.store.get_iter(i)

        if not icon:
            icon = self.get_system_thumbnail(fpath, self.iconFactory.SYS_ICON_WH[0])
            if not icon:
                if fpath.endswith(".gif"):
                    icon = GdkPixbuf.PixbufAnimation.get_static_image(fpath)
                else:
                    icon = GdkPixbuf.Pixbuf.new_from_file(self.iconFactory.INTERNAL_ICON_PTH)

        self.store.set_value(itr, 0, icon)

    def get_system_thumbnail(self, filename, size):
        try:
            if os.path.exists(filename):
                gioFile   = Gio.File.new_for_path(filename)
                info      = gioFile.query_info('standard::icon' , 0, Gio.Cancellable())
                icon      = info.get_icon().get_names()[0]
                iconTheme = Gtk.IconTheme.get_default()
                iconData  = iconTheme.lookup_icon(icon , size , 0)
                if iconData:
                    iconPath  = iconData.get_filename()
                    return GdkPixbuf.Pixbuf.new_from_file(iconPath)
                else:
                    return None
            else:
                return None
        except Exception as e:
            print("System icon generation issue:")
            print( repr(e) )
            return None


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
                self.self.settings.saveSettings(parentDir)
            elif isdir(file):
                self.currentPath = file
                self.setNewDirectory(self.currentPath)
                self.self.settings.saveSettings(self.currentPath)
            elif isfile(file):
                self.fileHandler.openFile(file)
        except Exception as e:
            print(e)

    def iconSingleClick(self, widget, eve, rclicked_icon):
        try:
            if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 1:
                self.selectedFiles.clear()
                items    = widget.get_selected_items()
                model    = widget.get_model()
                dir      = self.currentPath

                for item in items:
                    fileName = model[item][1]

                    if fileName != "." and fileName != "..":
                        file = dir + "/" + fileName
                        self.selectedFiles.append(file) # Used for return to caller

            elif eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == 3:
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
