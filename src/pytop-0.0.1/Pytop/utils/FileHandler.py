# Gtk imports

# Python imports
import os, shutil, subprocess, threading

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class FileHandler:
    def __init__(self, settings):
        # 'Filters'
        self.office = settings.returnOfficeFilter()
        self.vids   = settings.returnVidsFilter()
        self.txt    = settings.returnTextFilter()
        self.music  = settings.returnMusicFilter()
        self.images = settings.returnImagesFilter()
        self.pdf    = settings.returnPdfFilter()

        # Args
        self.MEDIAPLAYER  = settings.returnMediaProg()
        self.IMGVIEWER    = settings.returnImgVwrProg()
        self.MUSICPLAYER  = settings.returnMusicProg()
        self.OFFICEPROG   = settings.returnOfficeProg()
        self.TEXTVIEWER   = settings.returnTextProg()
        self.PDFVIEWER    = settings.returnPdfProg()
        self.FILEMANAGER  = settings.returnFileMngrProg()
        self.MPLAYER_WH   = settings.returnMplyrWH()
        self.MPV_WH       = settings.returnMpvWHProg()
        self.TRASHFILESFOLDER = settings.returnTrshFilesPth()
        self.TRASHINFOFOLDER  = settings.returnTrshInfoPth()



    @threaded
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


    def createFile(self, newFileName):
        pass

    def updateFile(self, oldFileName, newFileName):
        try:
            print("Renaming...")
            print(oldFileName + "  -->  " + newFileName)
            os.rename(oldFileName, newFileName)
            return 0
        except Exception as e:
            print("An error occured renaming the file:")
            print(e)
            return 1

    def moveToTrash(arg):
        try:
            print("Moving to Trash...")
            for file in toDeleteFiles:
                print(file)
                if os.path.exists(file):
                    shutil.move(file, self.TRASHFILESFOLDER)
                else:
                    print("The folder/file does not exist")
                    return 1
        except Exception as e:
            print("An error occured moving the file to trash:")
            print(e)
            return 1

        return 0

    def deleteFiles(self, toDeleteFiles):
        try:
            print("Deleting...")
            for file in toDeleteFiles:
                print(file)
                if os.path.exists(file):
                    if os.path.isfile(file):
                        os.remove(file)
                    elif os.path.isdir(file):
                        shutil.rmtree(file)
                    else:
                        print("An error occured deleting the file:")
                        return 1
                else:
                    print("The folder/file does not exist")
                    return 1
        except Exception as e:
            print("An error occured deleting the file:")
            print(e)
            return 1

        return 0

    def copyFile(self):
        pass

    def cutFile(self):
        pass

    def pasteFile(self):
        pass
