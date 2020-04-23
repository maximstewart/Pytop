# Python imports
import threading
from datetime import datetime

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

    def toggleCalPopover(self, widget, eve):
        calendarPopup = self.builder.get_object('calendarPopup')
        if (calendarPopup.get_visible() == False):
            calendarWid = self.builder.get_object('calendarWid')
            now         = datetime.now()
            timeStr     = now.strftime("%m/%d/%Y")
            parts       = timeStr.split("/")
            month       = int(parts[0])
            day         = int(parts[1])
            year        = int(parts[2])
            calendarWid.select_day(day)
            calendarWid.select_month(month, year)
            calendarPopup.popup()
        else:
            calendarPopup.popdown()


    def setPagerWidget(self):
        pager = wnck.Pager()

        if self.orientation == 0:
            self.builder.get_object('taskBarWorkspacesHor').add(pager)
        else:
            self.builder.get_object('taskBarWorkspacesVer').add(pager)

        pager.show()


    def setTasklistWidget(self):
        tasklist = wnck.Tasklist()
        tasklist.set_scroll_enabled(False)
        tasklist.set_button_relief(2)  # 0 = normal relief, 2 = no relief
        tasklist.set_grouping(1)       # 0 = mever group, 1 auto group, 2 = always group

        tasklist.set_orientation(self.orientation)
        if self.orientation == 0:
            self.builder.get_object('taskBarButtonsHor').add(tasklist)
        else:
            self.builder.get_object('taskBarButtonsVer').add(tasklist)

        tasklist.show()
