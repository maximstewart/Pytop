# Python imports
import threading

# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Wnck as wnck
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GLib

# Application imports


class TaskbarSignals:
    def __init__(self, settings):
        self.settings = settings
        self.builder  = self.settings.returnBuilder()

        self.setPagerWidget()
        self.setTasklistWidget()

    def setPagerWidget(self):
        pager = wnck.Pager()
        self.builder.get_object('taskBarWorkspaces').add(pager)

    def setTasklistWidget(self):
        barBtns = wnck.Tasklist()
        barBtns.set_button_relief(2)  # 0 = normal relief, 2 = no relief
        barBtns.set_grouping(1)  # 0 = mever group, 1 auto group, 2 = always group
        self.builder.get_object('taskBarButtons').add(barBtns)
