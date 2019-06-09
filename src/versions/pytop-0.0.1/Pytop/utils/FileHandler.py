
import subprocess


class FileHandler:
    def __init__(self):
        # 'Filters'
        self.office = ('.doc', '.docx', '.xls', '.xlsx', '.xlt', '.xltx' '.xlm', '.ppt', 'pptx', '.pps', '.ppsx', '.odt', '.rtf')
        self.vids   = ('.mkv', '.avi', '.flv', '.mov', '.m4v', '.mpg', '.wmv', '.mpeg', '.mp4', '.webm')
        self.txt    = ('.txt', '.text', '.sh', '.cfg', '.conf')
        self.music  = ('.psf', '.mp3', '.ogg' , '.flac')
        self.images = ('.png', '.jpg', '.jpeg', '.gif')
        self.pdf    = ('.pdf')

        # Args
        self.MEDIAPLAYER  = "mpv";
        self.IMGVIEWER    = "mirage";
        self.MUSICPLAYER  = "/opt/deadbeef/bin/deadbeef";
        self.OFFICEPROG   = "libreoffice";
        self.TEXTVIEWER   = "leafpad";
        self.PDFVIEWER    = "evince";
        self.FILEMANAGER  = "spacefm";
        self.MPLAYER_WH   = " -xy 1600 -geometry 50%:50% ";
        self.MPV_WH       = " -geometry 50%:50% ";


    def openFile(self, file):
        print("Opening: " + file)
        if file.lower().endswith(self.vids):
            subprocess.call([self.MEDIAPLAYER, self.MPV_WH, file])
        elif file.lower().endswith(self.music):
            subprocess.call([self.MUSICPLAYER, file])
        elif file.lower().endswith(self.images):
            subprocess.call([self.IMGVIEWER, file])
        elif file.lower().endswith(self.txt):
            subprocess.call([self.TEXTVIEWER, file])
        elif file.lower().endswith(self.pdf):
            subprocess.call([self.PDFVIEWER, file])
        elif file.lower().endswith(self.office):
            subprocess.call([self.OFFICEPROG, file])
        else:
            subprocess.call(['xdg-open', file])
