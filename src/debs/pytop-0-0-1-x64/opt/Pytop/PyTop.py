#!/usr/bin/python3

# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk as gtk
from gi.repository import WebKit2 as webkit

# Python imports
from utils import Settings, Events


class Main:
    def __init__(self):
        # Needed for glade file load to work right...
        webkit.WebView()

        self.builder     = gtk.Builder()
        self.settings    = Settings()
        self.settings.attachBuilder(self.builder)
        self.builder.connect_signals(Events(self.builder, self.settings))

        window = self.settings.createWindow()

        window.fullscreen()
        window.show_all()






if __name__ == "__main__":
    main = Main()
    gtk.main()
