#!/usr/bin/python3


# Python imports
import argparse
import pdb       # For trace debugging
from setproctitle import setproctitle

# Gtk imports
import gi, faulthandler, signal
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import GLib

# Application imports
from __init__ import Main



if __name__ == "__main__":
    try:
        # pdb.set_trace()
        setproctitle('Pytop')
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, gtk.main_quit)
        faulthandler.enable()  # For better debug info
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--file", "-f", default="default", help="JUST SOME FILE ARG.")

        # Read arguments (If any...)
        args = parser.parse_args()
        main = Main(args)
        gtk.main()
    except Exception as e:
        print( repr(e) )
