
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

        self.selectedFile = None



    def openFile(self, file):
        print("Opening: " + file)
        if file.lower().endswith(self.vids):
            subprocess.Popen([self.MEDIAPLAYER, self.MPV_WH, file])
        elif file.lower().endswith(self.music):
            subprocess.Popen([self.MUSICPLAYER, file])
        elif file.lower().endswith(self.images):
            subprocess.Popen([self.IMGVIEWER, file])
        elif file.lower().endswith(self.txt):
            subprocess.Popen([self.TEXTVIEWER, file])
        elif file.lower().endswith(self.pdf):
            subprocess.Popen([self.PDFVIEWER, file])
        elif file.lower().endswith(self.office):
            subprocess.Popen([self.OFFICEPROG, file])
        else:
            subprocess.Popen(['xdg-open', file])


    def renameFile(self, oldFileName, newFileName):
        try:
            print("Renaming...")
            print(oldFileName + "  -->  " + newFileName)
            return 0
        except Exception as e:
            print("An error occured renaming the file:")
            print(e)
            return 1

    def deleteFile(self, toDeleteFile):
        try:
            print("Deleting...")
            print(toDeleteFile)
            return 0
        except Exception as e:
            print("An error occured deleting the file:")
            print(e)
            return 1
