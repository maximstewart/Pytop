# Gtk imports
import gi, cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

# Python imports
import os

# Application imports


class Settings:
    def __init__(self):
        self.builder            = None

        # 'Filters'
        self.office = ('.doc', '.docx', '.xls', '.xlsx', '.xlt', '.xltx', '.xlm',
                                '.ppt', 'pptx', '.pps', '.ppsx', '.odt', '.rtf')
        self.vids   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv',
                                                    '.mpeg', '.mp4', '.webm')
        self.txt    = ('.txt', '.text', '.sh', '.cfg', '.conf')
        self.music  = ('.psf', '.mp3', '.ogg' , '.flac')
        self.images = ('.png', '.jpg', '.jpeg', '.gif')
        self.pdf    = ('.pdf')

        self.hideHiddenFiles    = True
        self.ColumnSize         = 8
        self.usrHome            = os.path.expanduser('~')
        self.desktopPath        = self.usrHome + "/Desktop"
        self.iconContainerWxH   = [128, 128]
        self.systemIconImageWxH = [72, 72]
        self.viIconWxH          = [256, 128]

        self.DEFAULTCOLOR     = gdk.RGBA(0.0, 0.0, 0.0, 0.0)   # ~#00000000
        self.MOUSEOVERCOLOR   = gdk.RGBA(0.0, 0.9, 1.0, 0.64)  # ~#00e8ff
        self.SELECTEDCOLOR    = gdk.RGBA(0.4, 0.5, 0.1, 0.84)
        self.TRASHFOLDER      = os.path.expanduser('~') + "/.local/share/Trash/"
        self.TRASHFILESFOLDER = self.TRASHFOLDER + "files/"
        self.TRASHINFOFOLDER  = self.TRASHFOLDER + "info/"
        self.THUMB_GENERATOR  = "ffmpegthumbnailer"
        self.MEDIAPLAYER      = "mpv";
        self.IMGVIEWER        = "mirage";
        self.MUSICPLAYER      = "/opt/deadbeef/bin/deadbeef";
        self.OFFICEPROG       = "libreoffice";
        self.TEXTVIEWER       = "leafpad";
        self.PDFVIEWER        = "evince";
        self.FILEMANAGER      = "spacefm";
        self.MPLAYER_WH       = " -xy 1600 -geometry 50%:50% ";
        self.MPV_WH           = " -geometry 50%:50% ";
        self.GTK_ORIENTATION  = 1   # HORIZONTAL (0) VERTICAL (1)

        if os.path.isdir(self.TRASHFOLDER) == False:
            os.mkdir(TRASHFILESFOLDER)
            os.mkdir(TRASHINFOFOLDER)

        if os.path.isdir(self.TRASHFILESFOLDER) == False:
            os.mkdir(TRASHFILESFOLDER)

        if os.path.isdir(self.TRASHINFOFOLDER) == False:
            os.mkdir(TRASHINFOFOLDER)


    def attachBuilder(self, builder):
        self.builder = builder
        self.builder.add_from_file("resources/PyTop.glade")

    def createWindow(self):
        # Get window and connect signals
        window = self.builder.get_object("Window")
        window.connect("delete-event", gtk.main_quit)
        self.setWindowData(window)
        return window

    def setWindowData(self, window):
        screen = window.get_screen()
        visual = screen.get_rgba_visual()
        if visual != None and screen.is_composited():
            window.set_visual(visual)

        # bind css file
        cssProvider = gtk.CssProvider()
        cssProvider.load_from_path('resources/stylesheet.css')
        screen = gdk.Screen.get_default()
        styleContext = gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, gtk.STYLE_PROVIDER_PRIORITY_USER)

        window.set_app_paintable(True)
        monitors = self.getMonitorData(screen)
        window.resize(monitors[0].width, monitors[0].height)

    def getMonitorData(self, screen):
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))

        for monitor in monitors:
            print(str(monitor.width) + "x" + str(monitor.height) + "+" + str(monitor.x) + "+" + str(monitor.y))

        return monitors


    def returnBuilder(self):             return self.builder
    def returnUserHome(self):            return self.usrHome
    def returnDesktopPath(self):         return self.usrHome + "/Desktop"
    def returnColumnSize(self):          return self.ColumnSize
    def returnContainerWH(self):         return self.iconContainerWxH
    def returnSystemIconImageWH(self):   return self.systemIconImageWxH
    def returnVIIconWH(self):            return self.viIconWxH
    def isHideHiddenFiles(self):         return self.hideHiddenFiles

    # Filter returns
    def returnOfficeFilter(self):        return self.office
    def returnVidsFilter(self):          return self.vids
    def returnTextFilter(self):          return self.txt
    def returnMusicFilter(self):         return self.music
    def returnImagesFilter(self):        return self.images
    def returnPdfFilter(self):           return self.pdf

    def returnIconImagePos(self):        return self.GTK_ORIENTATION
    def getThumbnailGenerator(self):     return self.THUMB_GENERATOR
    def returnMediaProg(self):           return self.MEDIAPLAYER
    def returnImgVwrProg(self):          return self.IMGVIEWER
    def returnMusicProg(self):           return self.MUSICPLAYER
    def returnOfficeProg(self):          return self.OFFICEPROG
    def returnTextProg(self):            return self.TEXTVIEWER
    def returnPdfProg(self):             return self.PDFVIEWER
    def returnFileMngrProg(self):        return self.FILEMANAGER
    def returnMplyrWH(self):             return self.MPLAYER_WH
    def returnMpvWHProg(self):           return self.MPV_WH
    def returnTrshFilesPth(self):        return self.TRASHFILESFOLDER
    def returnTrshInfoPth(self):         return self.TRASHINFOFOLDER
