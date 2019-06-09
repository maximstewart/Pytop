
# Gtk Imports
import gi
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk as gdk

# Python imports
import threading
from .Grid     import Grid
from .Dragging import Dragging
from threading import Thread


gdk.threads_init()
class Events:
    def __init__(self, settings):
        self.settings    = settings
        self.builder     = self.settings.returnBuilder()
        self.desktop     = self.builder.get_object("Desktop")
        self.webview     = self.builder.get_object("webview")
        self.desktopPath = self.settings.returnDesktopPath()

        self.settings.setDefaultWebviewSettings(self.webview, self.webview.get_settings())
        self.webview.load_uri(self.settings.returnWebHome())

        # Add filter to allow only folders to be selected
        selectedDirDialog = self.builder.get_object("selectedDirDialog")
        filefilter        = self.builder.get_object("Folders")
        selectedDirDialog.add_filter(filefilter)
        selectedDirDialog.set_filename(self.desktopPath)

        self.setDir(selectedDirDialog)


    def setDir(self, widget, data=None):
        newPath = widget.get_filename()
        Thread(target=Grid(self.desktop, self.settings).generateDirectoryGrid, args=(newPath,)).start()


    def showGridControlMenu(self, widget, data=None):
        popover = self.builder.get_object("gridControlMenu")
        popover.show_all()
        popover.popup()

    def showWebview(self, widget):
        self.builder.get_object("webViewer").popup()

    def loadHome(self, widget):
        self.webview.load_uri(self.settings.returnWebHome())

    def runSearchWebview(self, widget, data=None):
        if data.keyval == 65293:
            self.webview.load_uri(widget.get_text().strip())

    def refreshPage(self, widget, data=None):
        self.webview.load_uri(self.webview.get_uri())

    def setUrlBar(self, widget, data=None):
        self.builder.get_object("webviewSearch").set_text(widget.get_uri())
