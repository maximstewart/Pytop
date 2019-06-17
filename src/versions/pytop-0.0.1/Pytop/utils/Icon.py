
# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gio as gio
from gi.repository import GdkPixbuf
from xdg.DesktopEntry import DesktopEntry

# Python Imports
import os, subprocess, hashlib, threading
import urllib.request as urllib

from os.path import isdir, isfile, join



def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class Icon:
    def __init__(self, settings):
        self.settings           = settings
        self.thubnailGen        = self.settings.getThumbnailGenerator()

        self.GTK_ORIENTATION    = settings.returnIconImagePos()
        self.usrHome            = settings.returnUserHome()
        self.iconContainerWxH   = settings.returnContainerWH()
        self.systemIconImageWxH = settings.returnSystemIconImageWH()
        self.viIconWxH          = settings.returnVIIconWH()

        user_agent   = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
        self.headers = { 'User-Agent' : user_agent }


    def createIcon(self, dir, file):
        fullPath = dir + "/" + file
        thumbnl      = self.getIconImage(file, fullPath)
        return thumbnl

    def getIconImage(self, file, fullPath):
        thumbnl    = gtk.Image()
        vidsList   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        imagesList = ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.tga')

        try:
            if file.lower().endswith(vidsList): # Video thumbnail
                fileHash   = hashlib.sha256(str.encode(fullPath)).hexdigest()
                hashImgpth = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"

                if isfile(hashImgpth) == False:
                    self.generateVideoThumbnail(fullPath, hashImgpth)

                thumbnl = self.createIconImageBuffer(hashImgpth, self.viIconWxH)
            elif file.lower().endswith(imagesList):  # Image Icon
                thumbnl = self.createIconImageBuffer(fullPath, self.viIconWxH)
            else:  # System icons
                thumbnl = self.nonImageOrVideoIcon(fullPath)
        except Exception as e:
            print(e)
            return gtk.Image.new_from_file("resources/icons/bin.png")

        if thumbnl == None: # If no system icon, try stock file icon...
            thumbnl = gtk.Image.new_from_icon_name("gtk-file", gtk.IconSize.LARGE_TOOLBAR)
            if thumbnl == None:
                thumbnl = gtk.Image.new_from_file("resources/icons/bin.png")

        return thumbnl

    def nonImageOrVideoIcon(self, fullPath):
        if fullPath.lower().endswith( ('.desktop',) ):
            return self.parseDesktopFiles(fullPath)
        else:
            thumbPth = self.getSystemThumbnail(fullPath, self.systemIconImageWxH[0])
            return self.createIconImageBuffer(thumbPth, self.systemIconImageWxH)

    def createIconImageBuffer(self, path, wxh):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, wxh[0], wxh[1], False)
            return gtk.Image.new_from_pixbuf(pixbuf)
        except Exception as e:
            return gtk.Image.new_from_file("resources/icons/bin.png")

    def parseDesktopFiles(self, fullPath):
        xdgObj      = DesktopEntry(fullPath)
        icon        = xdgObj.getIcon()
        iconsDirs   = "/usr/share/icons"
        altIconPath = ""

        if "steam" in icon: # This whole thing is iffy at best but I want my damn icons!!
            steamIconsDir = self.usrHome + "/.thumbnails/steam_icons/"
            name          = xdgObj.getName()
            fileHash      = hashlib.sha256(str.encode(name)).hexdigest()

            if isdir(steamIconsDir) == False:
                os.mkdir(steamIconsDir)

            hashImgpth = steamIconsDir + fileHash + ".jpg"
            if isfile(hashImgpth) == True:
                return self.createIconImageBuffer(hashImgpth, self.systemIconImageWxH)

            execStr   = xdgObj.getExec()
            parts     = execStr.split("steam://rungameid/")
            id        = parts[len(parts) - 1]

            url       = "https://steamdb.info/app/" + id + "/"
            request   = urllib.Request(url, None, self.headers)
            response  = urllib.urlopen(request)
            page      = response.read().decode("utf8")
            response.close() # its always safe to close an open connection
            imageHTML = ""
            imageLink = ""

            for line in page.split("\n"):
                if "app-icon avatar" in line:
                    imageHTML = line.strip()
                    break

            srcPart    = imageHTML.split()
            srcPart    = srcPart[3].split("\"")
            imageLink  = srcPart[1]
            proc = subprocess.Popen(["wget", "-O", hashImgpth, imageLink])
            proc.wait()

            return self.createIconImageBuffer(hashImgpth, self.systemIconImageWxH)
        elif os.path.exists(icon):
            return self.createIconImageBuffer(icon, self.systemIconImageWxH)
        else:
            for (dirpath, dirnames, filenames) in os.walk(iconsDirs):
                for file in filenames:
                    appNM = "application-x-" + icon
                    if appNM in file:
                        altIconPath = dirpath + "/" + file
                        break

            return self.createIconImageBuffer(altIconPath, self.systemIconImageWxH)

    def getSystemThumbnail(self, filename, size):
        final_filename = ""
        if os.path.exists(filename):
            file = gio.File.new_for_path(filename)
            info = file.query_info('standard::icon' , 0 , gio.Cancellable())
            icon = info.get_icon().get_names()[0]

            icon_theme = gtk.IconTheme.get_default()
            icon_file = icon_theme.lookup_icon(icon , size , 0)
            if icon_file != None:
                final_filename = icon_file.get_filename()

            return final_filename

    def generateVideoThumbnail(self, fullPath, hashImgpth):
        proc = subprocess.Popen([self.thubnailGen, "-t", "65%", "-s", "300", "-c", "jpg", "-i", fullPath, "-o", hashImgpth])
        proc.wait()
