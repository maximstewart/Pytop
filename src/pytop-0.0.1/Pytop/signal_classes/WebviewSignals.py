# Gtk imports

# Python imports

# Application imports


class WebviewSignals:
    def __init__(self, settings):
        settings = settings
        builder       = settings.returnBuilder()

        self.webview       = builder.get_object("webview")
        self.webViewer     = builder.get_object("webViewer")
        self.webviewSearch = builder.get_object("webviewSearch")
        self.homePage      = settings.returnWebHome()

        settings.setDefaultWebviewSettings(self.webview, self.webview.get_settings())
        self.webview.load_uri(self.homePage)


    # Webview events
    def showWebview(self, widget):
        self.webViewer.popup()

    def loadHome(self, widget):
        self.webview.load_uri(self.homePage)

    def runSearchWebview(self, widget, data=None):
        if data.keyval == 65293:
            self.webview.load_uri(widget.get_text().strip())

    def refreshPage(self, widget, data=None):
        self.webview.load_uri(self.webview.get_uri())

    def setUrlBar(self, widget, data=None):
        self.webviewSearch.set_text(widget.get_uri())
