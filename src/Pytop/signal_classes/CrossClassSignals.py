# Python imports
from datetime import datetime

# Gtk imports
from gi.repository import GObject

# Application imports


class CrossClassSignals:
    def __init__(self, settings):
        self.settings     = settings
        self.builder      = self.settings.returnBuilder()
        self.timeLabel    = self.builder.get_object("timeLabel")
        self.displayclock()
        self.startClock()


    # Displays Timer
    def displayclock(self):
        now = datetime.now()
        hms = now.strftime("%I:%M %p")
        mdy = now.strftime("%m/%d/%Y")
        timeStr = hms + "\n" + mdy
        self.timeLabel.set_label(timeStr)
        return True

    # Starting or clock
    def startClock(self):
        GObject.timeout_add(59000, self.displayclock)


    def closePopup(self, widget, data=None):
        widget.hide()
