# Gtk imports

# Python imports

# Application imports
from widgets import Grid
from utils import Dragging
from utils import FileHandler


class Controller:
    def __init__(self, settings):
        self.filehandler  = FileHandler()
        self.settings     = settings
        self.builder      = self.settings.returnBuilder()
        self.desktop      = self.builder.get_object("Desktop")

        self.desktopPath  = self.settings.returnDesktopPath()
        self.grid         = None

        # Add filter to allow only folders to be selected
        selectedDirDialog = self.builder.get_object("selectedDirDialog")
        filefilter        = self.builder.get_object("Folders")
        selectedDirDialog.add_filter(filefilter)
        selectedDirDialog.set_filename(self.desktopPath)

        self.setIconViewDir(selectedDirDialog)

    def setIconViewDir(self, widget, data=None):
        newPath   = widget.get_filename()
        self.grid = Grid(self.desktop, self.settings)
        self.grid.setIconViewDir(newPath)

    def getWindowsOnScreen(self):
        screen        = self.settings.returnScren()
        windowButtons = self.builder.get_object("windowButtons")


    def closePopup(self, widget, data=None):
        widget.hide()



    # File control events
    def createFile(arg):
        pass

    def updateFile(self, file):
        if len(self.selectedFiles) == 1:
            newName = self.currentPath + "/" + file
            status  = self.filehandler.updateFile(self.selectedFiles[0], newName)

            if status == 0:
                self.selectedFiles = [newName]
                self.setIconViewDir(self.currentPath)


    def deleteFiles(self):
        if len(self.selectedFiles) == 1:
            status = self.filehandler.deleteFile(self.selectedFiles[0])

            if status == 0:
                self.selectedFiles = []
                self.setIconViewDir(self.currentPath)
        elif len(self.selectedFiles) > 1:
            pass


    def copyFile(self):
        pass

    def cutFile(self):
        pass

    def pasteFile(self):
        pass
