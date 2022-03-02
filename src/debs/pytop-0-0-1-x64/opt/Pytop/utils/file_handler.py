# Gtk imports

# Python imports
import os, shutil, subprocess, threading

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class FileHandler:
    def __init__(self, _settings):
        self.settings = _settings

        # 'Filters'
        self.office = self.settings.getOfficeFilter()
        self.vids   = self.settings.getVidsFilter()
        self.txt    = self.settings.getTextFilter()
        self.music  = self.settings.getMusicFilter()
        self.images = self.settings.getImagesFilter()
        self.pdf    = self.settings.getPdfFilter()

        # Args
        self.MEDIAPLAYER  = self.settings.getMediaProg()
        self.IMGVIEWER    = self.settings.getImgVwrProg()
        self.MUSICPLAYER  = self.settings.getMusicProg()
        self.OFFICEPROG   = self.settings.getOfficeProg()
        self.TEXTVIEWER   = self.settings.getTextProg()
        self.PDFVIEWER    = self.settings.getPdfProg()
        self.FILEMANAGER  = self.settings.getFileMngrProg()
        self.MPLAYER_WH   = self.settings.getMplyrWH()
        self.MPV_WH       = self.settings.getMpvWHProg()
        self.TRASHFILESFOLDER = self.settings.getTrshFilesPth()
        self.TRASHINFOFOLDER  = self.settings.getTrshInfoPth()


    def openFile(self, file):
        print("Opening: " + file)
        DEVNULL = open(os.devnull, 'w')

        if file.lower().endswith(self.vids):
            subprocess.Popen([self.MEDIAPLAYER, self.MPV_WH, file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        elif file.lower().endswith(self.music):
            subprocess.Popen([self.MUSICPLAYER, file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        elif file.lower().endswith(self.images):
            subprocess.Popen([self.IMGVIEWER, file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        elif file.lower().endswith(self.txt):
            subprocess.Popen([self.TEXTVIEWER, file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        elif file.lower().endswith(self.pdf):
            subprocess.Popen([self.PDFVIEWER, file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        elif file.lower().endswith(self.office):
            subprocess.Popen([self.OFFICEPROG, file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        else:
            subprocess.Popen(['xdg-open', file], start_new_session=True, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)


    def create(self, name, type):
        try:
            if type == True:     # Create File
                open(name, 'w')
            else:                # Create Folder
                os.mkdir(name)
        except Exception as e:
            print( repr(e) )
            return 1

        return 0

    def paste(self, files, toPath, pasteType):
        try:
            for file in files:
                parts       = file.split("/")
                toBePath    = toPath + "/" + parts[len(parts) - 1]  # Used to check for duplicates
                finalForm   = file + self.dedupPathIter(toBePath)
                isDuplicate = finalForm != file

                if isDuplicate:
                    os.rename(file, finalForm)

                if pasteType == 1:    # copy paste = 1
                    shutil.copy2(finalForm, toPath)
                    if isDuplicate:
                        os.rename(finalForm, file)  # Rename back after copy completes
                if pasteType == 2:    #  cut paste = 2
                    shutil.move(finalForm, toPath)

        except Exception as e:
            print( repr(e) )
            return 1

        return 0

    def delete(self, toDeleteFiles):
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
                    print("The folder/file does not exist")
                    return 1
        except Exception as e:
            print("An error occured deleting the file:")
            print( repr(e) )
            return 1

        return 0

    def trash(self, toTrashFiles):
        try:
            print("Moving to Trash...")
            for file in toTrashFiles:
                print(file)
                if os.path.exists(file):
                    parts         = file.split("/")
                    toBeTrashPath = self.TRASHFILESFOLDER + parts[len(parts) - 1]
                    finalForm     = file + self.dedupPathIter(toBeTrashPath)

                    if finalForm != file:
                        os.rename(file, finalForm)

                    shutil.move(finalForm, self.TRASHFILESFOLDER)
                else:
                    print("The folder/file does not exist")
                    return 1
        except Exception as e:
            print( repr(e) )
            return 1

        return 0

    def rename(self, oldFileName, newFileName):
        try:
            if os.path.exists(oldFileName):
                print("Renaming...")
                print(oldFileName + "  -->  " + newFileName)
                os.rename(oldFileName, newFileName)
            else:
                print("The folder/file does not exist")
                return 1
        except Exception as e:
            print( repr(e) )
            return 1

        return 0


    def dedupPathIter(self, toBeTrashPath):
        duplicateFix  = ""
        i             = 0

        if os.path.exists(toBeTrashPath):
            while os.path.exists(toBeTrashPath + duplicateFix) == True:
                i+=1
                duplicateFix = "-" + str(i)

        return duplicateFix
