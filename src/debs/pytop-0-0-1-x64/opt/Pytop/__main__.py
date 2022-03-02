#!/usr/bin/python3


# Python imports
import argparse, faulthandler, traceback
import pdb       # For trace debugging
from setproctitle import setproctitle

# Lib imports
import gi, faulthandler, signal
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

# Application imports
from main import Main



if __name__ == "__main__":
    try:
        # pdb.set_trace()
        setproctitle('Pytop')
        faulthandler.enable()  # For better debug info
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)

        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--file", "-f", default="default", help="JUST SOME FILE ARG.")
        # Read arguments (If any...)
        args, unknownargs = parser.parse_known_args()

        main = Main(args, unknownargs)
        Gtk.main()
    except Exception as e:
        traceback.print_exc()
