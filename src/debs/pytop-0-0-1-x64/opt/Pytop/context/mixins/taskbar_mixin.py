# Python imports
import threading
from datetime import datetime

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Wnck
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject

# Application imports



class MouseButton:
    LEFT_BUTTON   = 1
    MIDDLE_BUTTON = 2
    RIGHT_BUTTON  = 3


class TaskbarMixin:
    def toggleCalPopover(self, widget, eve):
        calendarPopup = self.builder.get_object('calendarPopup')
        if (calendarPopup.get_visible() == False):
            calendarWid = self.builder.get_object('calendarWid')
            now         = datetime.now()
            timeStr     = now.strftime("%m/%d/%Y")
            parts       = timeStr.split("/")
            month       = int(parts[0]) - 1
            day         = int(parts[1])
            year        = int(parts[2])
            calendarWid.select_day(day)
            calendarWid.select_month(month, year)
            calendarPopup.popup()
        else:
            calendarPopup.popdown()


    def showSystemStats(self, widget, eve):
        if eve.type == Gdk.EventType.BUTTON_RELEASE and eve.button == MouseButton.RIGHT_BUTTON:
            self.builder.get_object('systemStats').popup()

    def setPagerWidget(self):
        pager = Wnck.Pager()

        if self.orientation == 0:
            self.builder.get_object('taskBarWorkspacesHor').add(pager)
        else:
            self.builder.get_object('taskBarWorkspacesVer').add(pager)

        pager.show()


    def setTasklistWidget(self):
        tasklist = Wnck.Tasklist()
        tasklist.set_scroll_enabled(False)
        tasklist.set_button_relief(2)  # 0 = normal relief, 2 = no relief
        tasklist.set_grouping(1)       # 0 = mever group, 1 auto group, 2 = always group

        tasklist.set_orientation(self.orientation)
        if self.orientation == 0:
            self.builder.get_object('taskBarButtonsHor').add(tasklist)
        else:
            self.builder.get_object('taskBarButtonsVer').add(tasklist)

        tasklist.show()


    # Displays Timer
    def displayClock(self):
        now = datetime.now()
        hms = now.strftime("%I:%M %p")
        mdy = now.strftime("%m/%d/%Y")
        timeStr = hms + "\n" + mdy
        self.timeLabel.set_label(timeStr)
        return True

    # Starting or clock
    def startClock(self):
        GObject.timeout_add(59000, self.displayClock)


    def closePopup(self, widget, data=None):
        widget.hide()
