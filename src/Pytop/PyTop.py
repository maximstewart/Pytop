#!/usr/bin/python3

# Python imports
import inspect

from setproctitle import setproctitle

# Gtk imports
import gi, faulthandler, signal
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GLib

# Application imports
from utils import Settings
from signal_classes import CrossClassSignals, GridSignals, TaskbarSignals, DrawSignals


class Main:
    def __init__(self):
        setproctitle('Pytop')
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, gtk.main_quit)
        faulthandler.enable()  # For better debug info

        builder  = gtk.Builder()
        settings = Settings()
        settings.attachBuilder(builder)
        self.connectBuilder(settings, builder)

        window   = settings.createWindow()
        window.fullscreen()
        window.show()

        monitors = settings.returnMonitorsInfo()
        i = 1
        if len(monitors) > 1:
            for mon in monitors[1:]:
                subBuilder  = gtk.Builder()
                subSettings = Settings(i)
                subSettings.attachBuilder(subBuilder)
                self.connectBuilder(subSettings, subBuilder)

                win = subSettings.createWindow()
                win.set_default_size(mon.width, mon.height)
                win.set_size_request(mon.width, mon.height)
                win.set_resizable(False)


                win.move(mon.x, mon.y)
                win.show()
                i += 1


    def connectBuilder(self, settings, builder):
        # Gets the methods from the classes and sets to handler.
        # Then, builder connects to any signals it needs.
        classes  = [CrossClassSignals(settings),
                    GridSignals(settings),
                    TaskbarSignals(settings),
                    DrawSignals(settings)]

        handlers = {}
        for c in classes:
            methods = inspect.getmembers(c, predicate=inspect.ismethod)
            handlers.update(methods)

        builder.connect_signals(handlers)


if __name__ == "__main__":
    try:
        main = Main()
        gtk.main()
    except Exception as e:
        print(e)
