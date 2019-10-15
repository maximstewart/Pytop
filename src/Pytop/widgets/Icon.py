# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gio as gio
from xdg.DesktopEntry import DesktopEntry

# Python Imports
import os, subprocess, hashlib, threading
from os.path import isdir, isfile, join

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Icon:
    def __init__(self, settings):
        self.settings          = settings
        self.thubnailGen       = settings.getThumbnailGenerator()
        self.vidsList          = settings.returnVidsFilter()
        self.imagesList        = settings.returnImagesFilter()
        self.GTK_ORIENTATION   = settings.returnIconImagePos()
        self.usrHome           = settings.returnUserHome()
        self.iconContainerWH   = settings.returnContainerWH()
        self.systemIconImageWH = settings.returnSystemIconImageWH()
        self.viIconWH          = settings.returnVIIconWH()
        self.SCRIPT_PTH        = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.INTERNAL_ICON_PTH = self.SCRIPT_PTH + "../resources/icons/text.png"


    def createIcon(self, dir, file):
        fullPath = dir + "/" + file
        return self.getIconImage(file, fullPath)

    def createThumbnail(self, dir, file):
        fullPath = dir + "/" + file
        try:
            # Video thumbnail
            if file.lower().endswith(self.vidsList):
                fileHash   = hashlib.sha256(str.encode(fullPath)).hexdigest()
                hashImgPth = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"

                if isfile(hashImgPth) == False:
                    self.generateVideoThumbnail(fullPath, hashImgPth)

                thumbnl = self.createScaledImage(hashImgPth, self.viIconWH)

                if thumbnl == None: # If no icon whatsoever, return internal default
                    thumbnl = gtk.Image.new_from_file(self.SCRIPT_PTH + "../resources/icons/video.png")

            return thumbnl
        except Exception as e:
            print("Thumbnail generation issue:")
            print(e)
            return gtk.Image.new_from_file(self.SCRIPT_PTH + "../resources/icons/video.png")


    def getIconImage(self, file, fullPath):
        try:
            thumbnl = None

            # Video icon
            if file.lower().endswith(self.vidsList):
                thumbnl = gtk.Image.new_from_file(self.SCRIPT_PTH + "../resources/icons/video.png")
            # Image Icon
            elif file.lower().endswith(self.imagesList):
                thumbnl = self.createScaledImage(fullPath, self.viIconWH)
            # .desktop file parsing
            elif fullPath.lower().endswith( ('.desktop',) ):
                thumbnl = self.parseDesktopFiles(fullPath)
            # System icons
            else:
                thumbnl = self.getSystemThumbnail(fullPath, self.systemIconImageWH[0])

            if thumbnl == None: # If no icon whatsoever, return internal default
                thumbnl = gtk.Image.new_from_file(self.INTERNAL_ICON_PTH)

            return thumbnl
        except Exception as e:
            print("Icon generation issue:")
            print(e)
            return gtk.Image.new_from_file(self.INTERNAL_ICON_PTH)


    def parseDesktopFiles(self, fullPath):
        try:
            xdgObj      = DesktopEntry(fullPath)
            icon        = xdgObj.getIcon()
            iconsDirs   = "/usr/share/icons"
            altIconPath = ""

            if "steam" in icon:
                steamIconsDir = self.usrHome + "/.thumbnails/steam_icons/"
                name          = xdgObj.getName()
                fileHash      = hashlib.sha256(str.encode(name)).hexdigest()

                if isdir(steamIconsDir) == False:
                    os.mkdir(steamIconsDir)

                hashImgPth = steamIconsDir + fileHash + ".jpg"
                if isfile(hashImgPth) == True:
                    # Use video sizes since headers are bigger
                    return self.createScaledImage(hashImgPth, self.viIconWH)

                execStr   = xdgObj.getExec()
                parts     = execStr.split("steam://rungameid/")
                id        = parts[len(parts) - 1]

                # NOTE: Can try this logic instead...
                # if command exists use it instead of header image
                # if "steamcmd app_info_print id":
                #     proc = subprocess.Popen(["steamcmd", "app_info_print", id])
                #     proc.wait()
                # else:
                #     use the bottom logic

                imageLink = "https://steamcdn-a.akamaihd.net/steam/apps/" + id + "/header.jpg"
                proc      = subprocess.Popen(["wget", "-O", hashImgPth, imageLink])
                proc.wait()

                # Use video sizes since headers are bigger
                return self.createScaledImage(hashImgPth, self.viIconWH)
            elif os.path.exists(icon):
                return self.createScaledImage(icon, self.systemIconImageWH)
            else:
                for (dirpath, dirnames, filenames) in os.walk(iconsDirs):
                    for file in filenames:
                        appNM = "application-x-" + icon
                        if appNM in file:
                            altIconPath = dirpath + "/" + file
                            break

                return self.createScaledImage(altIconPath, self.systemIconImageWH)
        except Exception as e:
            print(".desktop icon generation issue:")
            print(e)
            return None


    def getSystemThumbnail(self, filename, size):
        try:
            if os.path.exists(filename):
                gioFile   = gio.File.new_for_path(filename)
                info      = gioFile.query_info('standard::icon' , 0, gio.Cancellable())
                icon      = info.get_icon().get_names()[0]
                iconTheme = gtk.IconTheme.get_default()
                iconData  = iconTheme.lookup_icon(icon , size , 0)
                if iconData:
                    iconPath  = iconData.get_filename()
                    return gtk.Image.new_from_file(iconPath)  # This seems to cause a lot of core dump issues...
                else:
                    return None
            else:
                return None
        except Exception as e:
            print("system icon generation issue:")
            print(e)
            return None


    def createScaledImage(self, path, wxh):
        try:
            pixbuf       = gtk.Image.new_from_file(path).get_pixbuf()
            scaledPixBuf = pixbuf.scale_simple(wxh[0], wxh[1], 2)  # 2 = BILINEAR and is best by default
            return gtk.Image.new_from_pixbuf(scaledPixBuf)
        except Exception as e:
            print("Image Scaling Issue:")
            print(e)
            return None

    def generateVideoThumbnail(self, fullPath, hashImgPth):
        try:
            proc = subprocess.Popen([self.thubnailGen, "-t", "65%", "-s", "300", "-c", "jpg", "-i", fullPath, "-o", hashImgPth])
            proc.wait()
        except Exception as e:
            print("Video thumbnail generation issue in thread:")
            print(e)
