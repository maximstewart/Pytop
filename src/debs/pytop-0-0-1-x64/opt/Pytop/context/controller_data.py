# Python imports
import os, signal

# Lib imports
from gi.repository import GLib

# Application imports
from plugins.plugins import Plugins

from widgets.grid import Grid
from widgets.icon import Icon
from utils.file_handler import FileHandler


class Controller_Data:
    ''' Controller_Data contains most of the state of the app at ay given time. It also has some support methods. '''

    def setup_controller_data(self, _settings):
        self.plugins        = Plugins(_settings)

        self.settings       = _settings
        self.builder        = self.settings.get_builder()

        self.timeLabel      = self.builder.get_object("timeLabel")
        self.drawArea       = self.builder.get_object("drawArea")
        self.brushSizeProp  = self.builder.get_object("brushSizeProp")
        self.brushColorProp = self.builder.get_object("brushColorProp")

        # Menu bar setup - Note: Must be before setting clock
        self.orientation = 1  # 0 = horizontal, 1 = vertical
        self.setPagerWidget()
        self.setTasklistWidget()

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
        self.filehandler   = FileHandler(self.settings)

        self.gridObj       = self.builder.get_object("Desktop")
        selectDirDialog    = self.builder.get_object("selectDirDialog")
        filefilter         = self.builder.get_object("Folders")

        self.currentPath   = self.settings.getSettings()[0]
        self.copyCutArry   = []
        self.selectedFiles = []
        self.gridClss      = Grid(self.gridObj, self.settings)
        self.pasteType     = 1  # copy == 1 and cut == 2


        # Add filter to allow only folders to be selected
        selectDirDialog.add_filter(filefilter)
        selectDirDialog.set_filename(self.currentPath)
        self.setNewDirectory(selectDirDialog)


        # Program Menu Parts
        self.menuWindow  = self.builder.get_object("menuWindow")
        self.menuWindow.set_keep_above(True);
        self.showIcons   = True

        self.iconFactory = Icon(self.settings)
        self.grpDefault  = "Accessories"
        self.progGroup   = self.grpDefault
        HOME_APPS        = f"{self.settings.get_user_home()}/.local/share/applications/"
        paths            = ["/opt/", "/usr/share/applications/", HOME_APPS]
        self.menuData    = self.getDesktopFilesInfo(paths)
        self.desktopObjs = []



    def clear_console(self):
        ''' Clears the terminal screen. '''
        os.system('cls' if os.name == 'nt' else 'clear')

    def call_method(self, _method_name, data = None):
        '''
        Calls a method from scope of class.

                Parameters:
                        a (obj): self
                        b (str): method name to be called
                        c (*): Data (if any) to be passed to the method.
                                Note: It must be structured according to the given methods requirements.

                Returns:
                        Return data is that which the calling method gives.
        '''
        method_name = str(_method_name)
        method      = getattr(self, method_name, lambda data: f"No valid key passed...\nkey={method_name}\nargs={data}")
        return method(data) if data else method()

    def has_method(self, obj, name):
        ''' Checks if a given method exists. '''
        return callable(getattr(obj, name, None))

    def clear_children(self, widget):
        ''' Clear children of a gtk widget. '''
        for child in widget.get_children():
            widget.remove(child)
