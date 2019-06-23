#!/usr/bin/python3

# Gtk imports
import gi, faulthandler, signal
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import WebKit2 as webkit
from gi.repository import GLib

# Python imports

# Application imports
from utils import Settings
from Controller import Controller


class Main:
    def __init__(self):
        faulthandler.enable()
        webkit.WebView()  # Needed for glade file to load...

        builder  = gtk.Builder()
        settings = Settings()
        settings.attachBuilder(builder)
        builder.connect_signals(Controller(settings))

        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, gtk.main_quit)

        window = settings.createWindow()
        window.fullscreen()
        window.show_all()


if __name__ == "__main__":
    try:
        main = Main()
        gtk.main()
    except Exception as e:
        print(e)
