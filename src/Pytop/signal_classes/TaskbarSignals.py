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
        self.orientation = 1  # 0 = horizontal, 1 = vertical

        self.setPagerWidget()
        self.setTasklistWidget()

    def setPagerWidget(self):
        pager = wnck.Pager()

        pager.set_orientation(self.orientation)
        if self.orientation == 0:
            self.builder.get_object('taskBarWorkspacesHor').add(pager)
        else:
            self.builder.get_object('taskBarWorkspacesVer').add(pager)


    def setTasklistWidget(self):
        barBtns = wnck.Tasklist()
        barBtns.set_scroll_enabled(False)
        barBtns.set_button_relief(2)  # 0 = normal relief, 2 = no relief
        barBtns.set_grouping(1)       # 0 = mever group, 1 auto group, 2 = always group

        barBtns.set_orientation(self.orientation)
        if self.orientation == 0:
            self.builder.get_object('taskBarButtonsHor').add(barBtns)
        else:
            self.builder.get_object('taskBarButtonsVer').add(barBtns)
