# Gtk imports

# Python imports

# Application imports


class CrossClassSignals:
    def __init__(self, settings):
        self.settings     = settings
        self.builder      = self.settings.returnBuilder()


    def closePopup(self, widget, data=None):
        widget.hide()
