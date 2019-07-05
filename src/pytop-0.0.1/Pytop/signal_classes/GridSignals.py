# Gtk imports

# Python imports

# Application imports
from widgets import Grid
from utils import Dragging
from utils import FileHandler


class GridSignals:
    def __init__(self, settings):
        self.settings     = settings
        self.filehandler  = FileHandler(settings)

        self.builder      = self.settings.returnBuilder()
        self.desktop      = self.builder.get_object("Desktop")
        selectedDirDialog = self.builder.get_object("selectedDirDialog")
        filefilter        = self.builder.get_object("Folders")

        self.desktopPath   = self.settings.returnDesktopPath()
        self.copyCutArry   = []
        self.selectedFiles = []
        self.grid          = None
        self.currentPath   = ""

        # Add filter to allow only folders to be selected
        selectedDirDialog.add_filter(filefilter)
        selectedDirDialog.set_filename(self.desktopPath)

        self.setIconViewDir(selectedDirDialog)


    def setIconViewDir(self, widget, data=None):
        newPath   = widget.get_filename()
        self.grid = Grid(self.desktop, self.settings)
        self.grid.setIconViewDir(newPath)


    # File control events
    def createFile(arg):
        pass

    def updateFile(self, widget, data):
        if data.keyval == 65293:  # Enter key press
            self.getGridInfo()
            file = widget.get_text();
            if len(self.selectedFiles) == 1:
                newName = self.currentPath + "/" + file
                status  = self.filehandler.updateFile(self.selectedFiles[0], newName)
                print("Old Name: " + self.selectedFiles[0])
                print("New Name: " + newName)

                if status == 0:
                    self.selectedFiles = [newName]
                    self.grid.setIconViewDir(self.currentPath)


    def trashFiles(self, widget):
        self.getGridInfo()
        status = self.filehandler.moveToTrash(self.selectedFiles)

        if status == 0:
            self.selectedFiles = []
            self.grid.setIconViewDir(self.currentPath)


    def deleteFiles(self, widget):
        self.getGridInfo()
        status = self.filehandler.deleteFiles(self.selectedFiles)

        if status == 0:
            self.selectedFiles = []
            self.grid.setIconViewDir(self.currentPath)

    def copy(self):
        self.copyCutArry = self.grid.returnSelectedFiles()

    def cut(self):
        self.copyCutArry = self.grid.returnSelectedFiles()

    def paste(self):
        self.currentPath = self.grid.returnCurrentPath()

    def getGridInfo(self):
        self.selectedFiles = self.grid.returnSelectedFiles()
        self.currentPath   = self.grid.returnCurrentPath()
