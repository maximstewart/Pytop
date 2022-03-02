# Python imports
import subprocess
import threading
import os
import json

from os.path import isdir, isfile, join
from os import listdir


# Lib imports
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GLib
from xdg.DesktopEntry import DesktopEntry


# Application imports




def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class MainMenuMixin:
    def toggleProgramMenu(self, widget):
        pos    = self.menuWindow.get_position()
        posX   = pos[0] + 32
        posY   = pos[1] + 72
        if self.menuWindow.get_visible() == False:
            self.menuWindow.move(posX, posY)
            GLib.idle_add(self.menuWindow.show_all)
        else:
            GLib.idle_add(self.menuWindow.hide)


    def setListGroup(self, widget):
        self.progGroup = widget.get_label().strip()
        self.getSubgroup(self.progGroup)
        self.generateListView()


    def searchForEntry(self, widget, data=None):
        self.progGroup = "[ Search ]"
        query          = widget.get_text().strip()
        if not query:
            self.progGroup   = self.grpDefault
            self.getSubgroup()
            self.generateListView()
            return

        self.getSubgroup(query)
        self.generateListView()


    def generateListView(self):
        widget = self.builder.get_object("programListBttns")

        # Should have this as a useful method...But, I don't want to import Glib everywhere
        children = widget.get_children()
        for child in children:
            GLib.idle_add(widget.remove, (child))

        for obj in self.desktopObjs:
            title   = obj[0]
            dirPath = obj[1]
            if self.showIcons:
                self.update_view(widget, title, dirPath)
            else:
                self.update_view(widget, title, dirPath)


    @threaded
    def update_view(self, widget, title, dirPath):
        image = self.iconFactory.parse_desktop_files(dirPath) # .get_pixbuf()
        if self.showIcons:
            GLib.idle_add(self.addToProgramListView, *(widget, title, image, self.showIcons,))
        else:
            GLib.idle_add(self.addToProgramListView, *(widget, title, image, self.showIcons,))


    def addToProgramListView(self, widget, title, image, show_image=True):
        icon   = Gtk.Image().new_from_pixbuf(image)
        button = Gtk.Button(label=title)

        if show_image:
            button.set_image(icon)
            button.set_always_show_image(True)
            pass

        button.connect("clicked", self.executeProgram)

        children   = button.get_children()
        alignment1 = children[0]
        box        = alignment1.get_children()[0]
        label      = box.get_children()[1]

        alignment1.set(0.0, 0.0, 0.0, 0.0)
        label.set_halign(1)
        label.set_line_wrap(True)
        label.set_max_width_chars(38)
        label.set_size_request(640, 64)

        button.show_all()
        widget.add(button)


    def executeProgram(self, widget):
        """
            # TODO:
                Need to refactor and pull out the sub loop that is used in both cases...
        """
        entry   = widget.get_label().strip()
        group   = self.progGroup

        parts   = entry.split("||")
        program = parts[0].strip()
        comment = parts[1].strip()

        if "[ Search ]" in group:
            gkeys = self.menuData.keys()
            for gkey in gkeys:
                for opt in self.menuData[gkey]:
                    if program in opt["title"]:
                        keys = opt.keys()
                        if comment in opt["comment"] or comment in opt["fileName"]:
                            DEVNULL = open(os.devnull, 'w')
                            execFailed = False
                            try:
                                command = opt["tryExec"].split("%")[0]
                                # self.logger.debug(command)
                                subprocess.Popen(command.split(), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
                                break
                            except Exception as e:
                                execFailed = True

                            if execFailed:
                                try:
                                    if "exec" in keys and len(opt["exec"]):
                                        command  = opt["exec"].split("%")[0]
                                        # self.logger.debug(command)
                                        subprocess.Popen(command.split(), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
                                        break
                                except Exception as e:
                                    print( repr(e) )
                                    # self.logger.debug(e)
        else:
            for opt in self.menuData[group]:
                if program in opt["title"]:
                    keys = opt.keys()
                    if comment in opt["comment"] or comment in opt["fileName"]:
                        DEVNULL = open(os.devnull, 'w')
                        execFailed = False
                        try:
                            command = opt["tryExec"].split("%")[0]
                            # self.logger.debug(command)
                            subprocess.Popen(command.split(), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
                        except Exception as e:
                            execFailed = True

                        if execFailed:
                            try:
                                if "exec" in keys and len(opt["exec"]):
                                    command  = opt["exec"].split("%")[0]
                                    # self.logger.debug(command)
                                    subprocess.Popen(command.split(), start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
                            except Exception as e:
                                print( repr(e) )
                                # self.logger.debug(e)


    # Supoport methods
    def getDesktopFilesInfo(self, paths):
        menuObjs = {
            "Accessories": [],
            "Multimedia": [],
            "Graphics": [],
            "Game": [],
            "Office": [],
            "Development": [],
            "Internet": [],
            "Settings": [],
            "System": [],
            "Wine": [],
            "Other": []
        }

        for path in paths:
            if not "/opt/" in path:
                self.listAndUpdateDesktopFiles(path, menuObjs);
            else:
                for folder in listdir(path):
                    try:
                        fPath = path + folder + "/"
                        self.listAndUpdateDesktopFiles(fPath, menuObjs);
                    except Exception as e:
                        print( repr(e) )

        return menuObjs

    def listAndUpdateDesktopFiles(self, path, menuObjs):
        for f in listdir(path):
            fPath = path + f
            if isfile(fPath) and f.endswith(".desktop"):
                xdgObj = DesktopEntry(fPath)

                title    = xdgObj.getName()
                groups   = xdgObj.getCategories()
                comment  = xdgObj.getComment()
                icon     = xdgObj.getIcon()
                mainExec = xdgObj.getExec()
                tryExec  = xdgObj.getTryExec()

                group    = ""
                if "Accessories" in groups or "Utility" in groups:
                    group = "Accessories"
                elif "Multimedia" in groups or "Video" in groups or "Audio" in groups:
                    group = "Multimedia"
                elif "Development" in groups:
                    group = "Development"
                elif "Game" in groups:
                    group = "Game"
                elif "Internet" in groups or "Network" in groups:
                    group = "Internet"
                elif "Graphics" in groups:
                    group = "Graphics"
                elif "Office" in groups:
                    group = "Office"
                elif "System" in groups:
                    group = "System"
                elif "Settings" in groups:
                    group = "Settings"
                elif "Wine" in groups:
                    group = "Wine"
                else:
                    group = "Other"

                menuObjs[group].append( {"title":  title,   "groups": groups,
                                        "comment": comment, "exec": mainExec,
                                        "tryExec": tryExec, "fileName": f,
                                        "filePath": fPath, "icon": icon})


    def getSubgroup(self, query = ""):
        """
            Need to refactor and pull out the sub logic that is used in both cases...
        """
        group = self.progGroup
        self.desktopObjs.clear()
        if "[ Search ]" in group:
            gkeys = self.menuData.keys()
            for gkey in gkeys:
                for opt in self.menuData[gkey]:
                    keys = opt.keys()

                    if "comment" in keys and len(opt["comment"]) > 0 :
                        if query.lower() in opt["comment"].lower():
                            title = opt["title"] + " || " + opt["comment"]
                            fPath = opt["filePath"]
                            self.desktopObjs.append([title, fPath])
                            continue

                    if query.lower() in opt["title"].lower() or \
                        query.lower() in opt["fileName"].lower():
                        title = opt["title"] + " || " + opt["fileName"].replace(".desktop", "")
                        fPath  = opt["filePath"]
                        self.desktopObjs.append([title, fPath])
        else:
            for opt in self.menuData[group]:
                keys = opt.keys()
                if "comment" in keys and len(opt["comment"]) > 0 :
                    title = opt["title"] + " || " + opt["comment"]
                    fPath  = opt["filePath"]
                    self.desktopObjs.append([title, fPath])
                else:
                    title = opt["title"] + " || " + opt["fileName"].replace(".desktop", "")
                    fPath  = opt["filePath"]
                    self.desktopObjs.append([title, fPath])

        return self.desktopObjs
