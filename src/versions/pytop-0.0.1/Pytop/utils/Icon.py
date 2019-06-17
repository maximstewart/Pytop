
# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gio as gio
from gi.repository import GdkPixbuf

import os, subprocess, hashlib, threading
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

    def createIcon(self, dir, file):
        fullPath = dir + "/" + file
        thumbnl      = self.getIconImage(file, fullPath)
        return thumbnl

    def getIconImage(self, file, fullPath):
        thumbnl    = gtk.Image()
        vidsList   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        imagesList = ('.png', '.jpg', '.jpeg', '.gif')

        try:
            if file.lower().endswith(vidsList):
                fileHash   = hashlib.sha256(str.encode(fullPath)).hexdigest()
                hashImgpth = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"

                if isfile(hashImgpth) == False:
                    self.generateVideoThumbnail(fullPath, hashImgpth)

                thumbnl = self.createIconImageBuffer(hashImgpth, self.viIconWxH)
            elif file.lower().endswith(imagesList):
                thumbnl = self.createIconImageBuffer(fullPath, self.viIconWxH)
            else:
                thumbnl = self.nonImageOrVideoIcon(fullPath)
        except Exception as e:
            return gtk.Image.new_from_file("resources/icons/bin.png")

        if thumbnl == None: # If no system icon, try stock file icon...
            thumbnl = gtk.Image.new_from_icon_name("gtk-file", gtk.IconSize.LARGE_TOOLBAR)
            if thumbnl == None:
                thumbnl = gtk.Image.new_from_file("resources/icons/bin.png")

        return thumbnl

    def nonImageOrVideoIcon(self, fullPath):
        thumbPth = self.getSystemThumbnail(fullPath, self.systemIconImageWxH[0])
        return self.createIconImageBuffer(thumbPth, self.systemIconImageWxH)

    def createIconImageBuffer(self, path, wxh):
        pixbuf = None
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
              filename  = path,
              width     = wxh[0],
              height    = wxh[1],
              preserve_aspect_ratio = False)
            return gtk.Image.new_from_pixbuf(pixbuf)
        except Exception as e:
            return gtk.Image.new_from_file("resources/icons/bin.png")

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
