# Python imports
from datetime import datetime
import os

# Gtk imports


# Application imports
from .controller_data        import Controller_Data
from .mixins.main_menu_mixin import MainMenuMixin
from .mixins.taskbar_mixin   import TaskbarMixin
from .mixins.cpu_draw_mixin  import CPUDrawMixin
from .mixins.grid_mixin      import GridMixin





class Controller(CPUDrawMixin, MainMenuMixin, TaskbarMixin, GridMixin, Controller_Data):
    def __init__(self, _settings):
        self.setup_controller_data(_settings)
