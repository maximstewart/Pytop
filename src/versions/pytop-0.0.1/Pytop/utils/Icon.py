
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
        fullPathFile = dir + "/" + file
        thumbnl      = self.getIconImage(file, fullPathFile)
        return thumbnl

    def getIconImage(self, file, fullPathFile):
        thumbnl    = gtk.Image()
        vidsList   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        imagesList = ('.png', '.jpg', '.jpeg', '.gif')

        if file.lower().endswith(vidsList):
            fileHash   = hashlib.sha256(str.encode(fullPathFile)).hexdigest()
            hashImgpth = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"

            # Generate any thumbnails beforehand...
            try:
                if isfile(hashImgpth) == False:
                    self.generateVideoThumbnail(fullPathFile, hashImgpth)
                    thumbnl = self.createIconImageBuffer(hashImgpth, self.viIconWxH)
                else:
                    thumbnl = self.createIconImageBuffer(hashImgpth, self.viIconWxH)
            except Exception as e:
                print(e)
                thumbPth = self.getSystemThumbnail(fullPathFile, self.systemIconImageWxH[0])
                thumbnl  = self.createIconImageBuffer(thumbPth, self.systemIconImageWxH)

        elif file.lower().endswith(imagesList):
            thumbnl = self.createIconImageBuffer(fullPathFile, self.viIconWxH)
        else:
            thumbPth = self.getSystemThumbnail(fullPathFile, self.systemIconImageWxH[0])
            thumbnl  = self.createIconImageBuffer(thumbPth, self.systemIconImageWxH)

        # NOTE: Returning pixbuf through retreval to keep this file more universaly usable.
        # We can just remove get_pixbuf to get a gtk image
        return thumbnl.get_pixbuf()

    def createIconImageBuffer(self, path, wxh):
        pixbuf = None
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename  = path,
            width     = wxh[0],
            height    = wxh[1],
            preserve_aspect_ratio = True)
            return gtk.Image.new_from_pixbuf(pixbuf)
        except Exception as e:
            print(e)

        return gtk.Image()

    def getSystemThumbnail(self, filename,size):
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

    def generateVideoThumbnail(self, fullPathFile, hashImgpth):
        proc = subprocess.Popen([self.thubnailGen, "-t", "65%", "-s", "300", "-c", "jpg", "-i", fullPathFile, "-o", hashImgpth])
        proc.wait()
