# Gtk imports
import gi, cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk

# Python imports
import os, json

# Application imports
from .logger import Logger


class Settings:
    def __init__(self, monIndex = 0):

        self._USR_PATH        = f"/usr/share/{app_name.lower()}"
        self._USER_HOME       = os.path.expanduser('~')
        self._SCRIPT_PTH      = os.path.dirname(os.path.realpath(__file__))
        self._DESKTOP_PATH    = f"{self._USER_HOME}/Desktop"
        self._CONFIG_PATH     = f"{self._USER_HOME}/.config/{app_name.lower()}"
        self._CONFIG_FILE     = f"{self._CONFIG_PATH}/mon_{str(monIndex)}_settings.ini"
        self._PLUGINS_PATH    = f"{self._CONFIG_PATH}/plugins"
        self._LOGGER          = Logger(self._USER_HOME)

        self._DEFAULT_ICONS     = f"{self._CONFIG_PATH}/icons"
        self._INTERNAL_ICON_PTH = f"{self._DEFAULT_ICONS}/bin.png"
        self._ABS_THUMBS_PTH    = f"{self._USER_HOME}/.thumbnails/normal"
        self._STEAM_ICONS_PTH   = f"{self._USER_HOME}/.thumbnails/steam_icons"
        self._ICON_DIRS         = ["/usr/share/icons", f"{self._USER_HOME}/.local/share/icons"]

        self.DEFAULTCOLOR     = Gdk.RGBA(0.0, 0.0, 0.0, 0.0)   # ~#00000000
        self.MOUSEOVERCOLOR   = Gdk.RGBA(0.0, 0.9, 1.0, 0.64)  # ~#00e8ff
        self.SELECTEDCOLOR    = Gdk.RGBA(0.4, 0.5, 0.1, 0.84)
        self._TRASHFOLDER     = f"{self._USER_HOME}/.local/share/Trash"
        self._TRASH_FILES_FOLDER = f"{self._TRASHFOLDER}/files/"
        self._TRASH_INFO_FOLDER  = f"{self._TRASHFOLDER}/info/"
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
        self.iconContainerWxH   = [128, 128]
        self.systemIconImageWxH = [56, 56]
        self.viIconWxH          = [256, 128]
        self.monitors           = None
        self.builder            = None

        if os.path.isdir(self._CONFIG_PATH) == False:
            os.mkdir(self._CONFIG_PATH)

        if os.path.isdir(self._TRASHFOLDER) == False:
            os.mkdir(TRASHFILESFOLDER)
            os.mkdir(TRASHINFOFOLDER)

        if os.path.isdir(self._TRASH_FILES_FOLDER) == False:
            os.mkdir(TRASHFILESFOLDER)

        if os.path.isdir(self._TRASH_INFO_FOLDER) == False:
            os.mkdir(TRASHINFOFOLDER)

        if os.path.isfile(self._CONFIG_FILE) == False:
            open(self._CONFIG_FILE, 'a').close()
            self.saveSettings(self._DESKTOP_PATH)


    def attach_builder(self, builder):
        self.builder = builder
        self.builder.add_from_file(f"{self._CONFIG_PATH}/Main_Window.glade")

    def create_window(self):
        # Get window and connect signals
        window = self.builder.get_object("Window")
        window.connect("delete-event", Gtk.main_quit)
        self.set_window_data(window)
        return window

    def set_window_data(self, window):
        screen = window.get_screen()
        visual = screen.get_rgba_visual()
        if visual != None and screen.is_composited():
            window.set_visual(visual)

        # bind css file
        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path(f'{self._CONFIG_PATH}/stylesheet.css')
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        window.set_app_paintable(True)
        self.monitors = self.get_monitor_data(screen)

    def get_monitor_data(self, screen):
        monitors = []
        for m in range(screen.get_n_monitors()):
            monitors.append(screen.get_monitor_geometry(m))

        for monitor in monitors:
            print(str(monitor.width) + "+" + str(monitor.height) + "+" + str(monitor.x) + "+" + str(monitor.y))

        return monitors


    def get_monitor_info(self):
        return self.monitors


    def saveSettings(self, startPath):
        data = {}
        data['pytop_settings'] = []

        data['pytop_settings'].append({
          'startPath' : startPath
        })

        with open(self._CONFIG_FILE, 'w') as outfile:
            json.dump(data, outfile)


    def getSettings(self):
        returnData = []

        with open(self._CONFIG_FILE) as infile:
            try:
                data = json.load(infile)
                for obj in data['pytop_settings']:
                    returnData = [obj['startPath']]
            except Exception as e:
                returnData = [f'{self._DESKTOP_PATH}']


        if returnData[0] == '':
            returnData[0] = f'{self._DESKTOP_PATH}'

        return returnData


    def get_builder(self):            return self.builder
    def get_user_home(self):          return self._USER_HOME

    def get_desktop_path(self):       return self._DESKTOP_PATH
    def get_config_path(self):        return self._CONFIG_PATH
    def get_plugins_path(self):       return self._PLUGINS_PATH

    def getColumnSize(self):          return self.ColumnSize
    def getContainerWH(self):         return self.iconContainerWxH
    def getSystemIconImageWH(self):   return self.systemIconImageWxH
    def getVIIconWH(self):            return self.viIconWxH
    def isHideHiddenFiles(self):      return self.hideHiddenFiles

    # Filter returns
    def getOfficeFilter(self):        return self.office
    def getVidsFilter(self):          return self.vids
    def getTextFilter(self):          return self.txt
    def getMusicFilter(self):         return self.music
    def getImagesFilter(self):        return self.images
    def getPdfFilter(self):           return self.pdf

    def getIconImagePos(self):        return self.GTK_ORIENTATION
    def getThumbnailGenerator(self):  return self.THUMB_GENERATOR
    def getMediaProg(self):           return self.MEDIAPLAYER
    def getImgVwrProg(self):          return self.IMGVIEWER
    def getMusicProg(self):           return self.MUSICPLAYER
    def getOfficeProg(self):          return self.OFFICEPROG
    def getTextProg(self):            return self.TEXTVIEWER
    def getPdfProg(self):             return self.PDFVIEWER
    def getFileMngrProg(self):        return self.FILEMANAGER
    def getMplyrWH(self):             return self.MPLAYER_WH
    def getMpvWHProg(self):           return self.MPV_WH
    def getTrshFilesPth(self):        return self._TRASH_FILES_FOLDER
    def getTrshInfoPth(self):         return self._TRASH_INFO_FOLDER

    def getDefaultIcon(self):         return self._INTERNAL_ICON_PTH
    def getInternalIconsPth(self):    return self._DEFAULT_ICONS
    def getAbsThumbsPth(self):        return self._ABS_THUMBS_PTH
    def getSteamIconsPth(self):       return self._STEAM_ICONS_PTH
    def getIconDirs(self):            return self._ICON_DIRS
