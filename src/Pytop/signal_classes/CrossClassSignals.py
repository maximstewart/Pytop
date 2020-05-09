# Python imports
from datetime import datetime

# Gtk imports
from gi.repository import GObject

# Application imports
from mixins import CPUDrawMixin, TaskbarMixin


class CrossClassSignals(CPUDrawMixin, TaskbarMixin):
    def __init__(self, settings):
        self.settings       = settings
        self.builder        = self.settings.returnBuilder()

        self.timeLabel      = self.builder.get_object("timeLabel")
        self.drawArea       = self.builder.get_object("drawArea")
        self.brushSizeProp  = self.builder.get_object("brushSizeProp")
        self.brushColorProp = self.builder.get_object("brushColorProp")

        # Menu bar setup
        self.orientation = 1  # 0 = horizontal, 1 = vertical

        # Must be before setting clock
        self.setPagerWidget()
        self.setTasklistWidget()

        # Must be after pager and task list inits
        self.displayclock()
        self.startClock()

        # CPUDrawMixin Parts
        self.cpu_percents     = []
        self.doDrawBackground = False
        self.isDrawing        = False
        self.surface          = None
        self.aw               = None  # Draw area width
        self.ah               = None  # Draw area height
        self.xStep            = None  # For x-axis 60 sec steps
        self.yStep            = None  # For y-axis %s

        rgba                  = self.brushColorProp.get_rgba()
        self.brushColorVal    = [rgba.red, rgba.green, rgba.blue, rgba.alpha]
        self.brushSizeVal     = self.brushSizeProp.get_value()
        self.updateSpeed      = 100 # 1 sec = 1000ms

        self.good             = [0.53, 0.8, 0.15, 1.0]
        self.warning          = [1.0, 0.66, 0.0, 1.0]
        self.danger           = [1.0, 0.0, 0.0, 1.0]




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
