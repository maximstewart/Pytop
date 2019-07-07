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
        self.pasteType     = 1  # copy == 1 and cut == 2

        # Add filter to allow only folders to be selected
        selectedDirDialog.add_filter(filefilter)
        selectedDirDialog.set_filename(self.desktopPath)
        self.setIconViewDir(selectedDirDialog)


    def setIconViewDir(self, widget, data=None):
        newPath   = widget.get_filename()
        self.grid = Grid(self.desktop, self.settings)
        self.grid.setIconViewDir(newPath)


    # File control events
    def create(self, wdget):
        self.currentPath = self.grid.returnCurrentPath()
        fileName         = self.builder.get_object("filenameInput").get_text().strip()
        type             = self.builder.get_object("createSwitch").get_state()

        if fileName != "":
            fileName = self.currentPath + "/" + fileName
            status = self.filehandler.create(fileName, type)
            if status == 0:
                self.grid.setIconViewDir(self.currentPath)

    def copy(self, widget):
        self.pasteType   = 1
        self.copyCutArry = self.grid.returnSelectedFiles()

    def cut(self, widget):
        self.pasteType   = 2
        self.copyCutArry = self.grid.returnSelectedFiles()

    def paste(self, widget):
        print(len(self.copyCutArry))
        self.currentPath = self.grid.returnCurrentPath()
        status           =  self.filehandler.paste(self.copyCutArry, self.currentPath, self.pasteType)
        if status == 0:
            self.grid.setIconViewDir(self.currentPath)
            if self.pasteType == 2:  # cut == 2
                self.copyCutArry = []

    def delete(self, widget):
        self.getGridInfo()
        status = self.filehandler.delete(self.selectedFiles)

        if status == 0:
            self.selectedFiles = []
            self.grid.setIconViewDir(self.currentPath)

    def trash(self, widget):
        self.getGridInfo()
        status = self.filehandler.trash(self.selectedFiles)

        if status == 0:
            self.selectedFiles = []
            self.grid.setIconViewDir(self.currentPath)

    def rename(self, widget, data):
        if data.keyval == 65293:  # Enter key press
            self.getGridInfo()
            file = widget.get_text();
            if len(self.selectedFiles) == 1:
                newName = self.currentPath + "/" + file
                print("Old Name: " + self.selectedFiles[0])
                print("New Name: " + newName.strip())

                status  = self.filehandler.rename(self.selectedFiles[0], newName.strip())
                if status == 0:
                    self.selectedFiles = [newName]
                    self.grid.setIconViewDir(self.currentPath)

    def getGridInfo(self):
        self.selectedFiles = self.grid.returnSelectedFiles()
        self.currentPath   = self.grid.returnCurrentPath()
