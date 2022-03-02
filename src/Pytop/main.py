# Python imports
import inspect

# Lib imports
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

# Application imports
from utils.settings import Settings
from context.controller import Controller
from __builtins__ import EventSystem


class Main(EventSystem):
    def __init__(self, args, unknownargs):
        settings = Settings()
        settings.set_window_data(Gtk.Window())
        monitors = settings.get_monitor_info()
        for i, mon in enumerate(monitors):
            sub_builder  = Gtk.Builder()
            sub_settings = Settings(i)
            sub_settings.attach_builder(sub_builder)
            self.connect_builder(sub_settings, sub_builder)

            window = sub_settings.create_window()
            window.set_default_size(mon.width, mon.height)
            window.set_size_request(mon.width, mon.height)
            window.set_resizable(False)
            window.resize(mon.width, mon.height)
            window.move(mon.x, mon.y)
            window.show()



    def connect_builder(self, settings, builder):
        # Gets the methods from the classes and sets to handler.
        # Then, builder connects to any signals it needs.
        classes  = [Controller(settings)]

        handlers = {}
        for c in classes:
            methods = inspect.getmembers(c, predicate=inspect.ismethod)
            handlers.update(methods)

        builder.connect_signals(handlers)
