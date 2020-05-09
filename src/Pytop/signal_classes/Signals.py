# Python imports
from datetime import datetime

# Gtk imports


# Application imports
from .mixins import CPUDrawMixin, TaskbarMixin, GridMixin
from utils import FileHandler


class Signals(CPUDrawMixin, TaskbarMixin, GridMixin):
    def __init__(self, settings):
        self.settings       = settings
        self.builder        = self.settings.returnBuilder()

        self.timeLabel      = self.builder.get_object("timeLabel")
        self.drawArea       = self.builder.get_object("drawArea")
        self.brushSizeProp  = self.builder.get_object("brushSizeProp")
        self.brushColorProp = self.builder.get_object("brushColorProp")

        # Menu bar setup - Note: Must be before setting clock
        self.orientation = 1  # 0 = horizontal, 1 = vertical
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


        # GridMixin Parts
        self.filehandler   = FileHandler(settings)

        self.builder       = self.settings.returnBuilder()
        self.gridObj       = self.builder.get_object("Desktop")
        selectDirDialog    = self.builder.get_object("selectDirDialog")
        filefilter         = self.builder.get_object("Folders")

        self.currentPath   = self.settings.returnSettings()[0]
        self.copyCutArry   = []
        self.selectedFiles = []
        self.gridClss      = None
        self.pasteType     = 1  # copy == 1 and cut == 2

        # Add filter to allow only folders to be selected
        selectDirDialog.add_filter(filefilter)
        selectDirDialog.set_filename(self.currentPath)
        self.setNewDirectory(selectDirDialog)
