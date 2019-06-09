
# Gtk Imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk as gtk
from gi.repository import Gio as gio
from gi.repository import GdkPixbuf

import os, hashlib
from os.path import isdir, isfile, join


class Icon:
    def __init__(self):
        self.GTK_ORIENTATION = 1   # HORIZONTAL (0) VERTICAL (1)
        self.iconImageWxH    = [64, 64]
        self.iconWxH         = [128, -1]
        self.iconMargins     = 8
        self.usrHome         = os.path.expanduser('~')


    def createIcon(self, dir, file):
        fullPathFile = dir + "/" + file
        eveBox       = gtk.EventBox()
        icon         = gtk.Box()
        label        = gtk.Label()
        thumbnl      = self.defineIconImage(file, fullPathFile)

        label.set_max_width_chars(1)
        label.set_ellipsize(3)       # ELLIPSIZE_END (3)
        label.set_lines(2)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(2)  # WRAP_WORD (0)  WRAP_CHAR (1)  WRAP_WORD_CHAR (2)
        label.set_width_chars(1)
        label.set_text(file)

        icon.set_size_request(self.iconWxH[0], self.iconWxH[1]);
        icon.set_property('orientation', self.GTK_ORIENTATION)
        icon.add(thumbnl)
        icon.add(label)

        eveBox.add(icon)
        eveBox.show_all()
        return eveBox

    def defineIconImage(self, file, fullPathFile):
        thumbnl    = gtk.Image()
        vidsList   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        imagesList = ('.png', '.jpg', '.jpeg', '.gif')

        if file.lower().endswith(vidsList):
            fileHash   = hashlib.sha256(str.encode(fullPathFile)).hexdigest()
            hashImgpth = self.usrHome + "/.thumbnails/normal/" + fileHash + ".png"
            if isfile(hashImgpth) == False:
                self.generateThumbnail(fullPathFile, hashImgpth)

            thumbnl = self.createGtkImage(hashImgpth, self.iconImageWxH)
        elif file.lower().endswith(imagesList):
            thumbnl = self.createGtkImage(fullPathFile, self.iconImageWxH)
        else:
            thumbPth = self.getSystemThumbnail(fullPathFile, self.iconImageWxH[0])
            thumbnl  = self.createGtkImage(thumbPth, self.iconImageWxH)

        return thumbnl

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

    def generateThumbnail(self, fullPathFile, hashImgpth):
        subprocess.call(["ffmpegthumbnailer", "-t", "65%", "-s", "300", "-c", "jpg", "-i", fullPathFile, "-o", hashImgpth])

    def createGtkImage(self, path, wxh):
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