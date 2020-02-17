# Gtk imports
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Wnck as wnck
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GLib


# Python imports
import threading

# Application imports



def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper

class MouseButtons:
    LEFT_BUTTON  = 1
    RIGHT_BUTTON = 3


class TaskbarSignals:
    def __init__(self, settings):
        self.settings           = settings
        self.builder            = self.settings.returnBuilder()
        self.taskBarButtons     = self.builder.get_object('taskBarButtons')
        self.taskbarMenu        = self.builder.get_object('taskbarMenu')

        self.SCREEN             = wnck.Screen.get_default()
        self.actv_workspace_num = None
        self.window             = None

        self.SCREEN.force_update() # (Re)populate screen windows list
        self.refreashTaskbar()
        self.setScreenSignals()
        self.setPagerWidget()


    def refreashTaskbar(self):
        workspace = self.SCREEN.get_active_workspace()
        self.actv_workspace_num = workspace.get_number()

        windows = self.SCREEN.get_windows()
        for w in windows:
            if workspace and w.get_workspace():
                wnum = w.get_workspace().get_number()
                if not w.is_skip_pager() and not w.is_skip_tasklist() and wnum == self.actv_workspace_num:
                    btn = self.createWinBttn(w)
                    self.setupSignals(btn, w)
                    self.taskBarButtons.add(btn)

    def setupSignals(self, btn, win):
        btn.connect("button-press-event", self.clickEvent, (win))

    def setScreenSignals(self):
        self.SCREEN.connect("active-workspace-changed", self.activeWorkspaceChanged)
        self.SCREEN.connect("window-opened", self.windowOpened)
        self.SCREEN.connect("window-closed", self.windowClosed)

    def createWinBttn(self, w):
        btn = gtk.Button(label=w.get_name(), always_show_image=True)
        img = gtk.Image()
        img.set_from_pixbuf( w.get_icon() )  # w.get_mini_icon() or  w.get_icon()
        btn.set_image(img)
        btn.show()
        return btn

    def clickEvent(self, widget, e, window):
        if e.type == gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.LEFT_BUTTON:
            if window.is_minimized():
                window.activate(1)
            else:
                window.minimize()
        if e.type == gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.RIGHT_BUTTON:
            self.window = window
            self.setTaskbarMenuStates()
            self.taskbarMenu.show()

    def setTaskbarMenuStates(self):
        if not self.window.is_above(): # If above all windows
            self.builder.get_object("alwaysOnTopToggle").set_active(False)
        else:
            self.builder.get_object("alwaysOnTopToggle").set_active(True)

        if not self.window.is_below(): # If below all windows
            self.builder.get_object("alwaysBelowToggle").set_active(False)
        else:
            self.builder.get_object("alwaysBelowToggle").set_active(True)

        if not self.window.is_pinned(): # If visable on all workspaces
            self.builder.get_object("alwaysOnVisableWorkspace").set_active(False)
        else:
            self.builder.get_object("alwaysOnVisableWorkspace").set_active(True)

        if not self.window.is_sticky(): # If visable on all workspaces??
            pass
        else:
            pass

        if not self.window.is_active(): # If window has focus
            pass
        else:
            pass


    def hideTaskbarMenu(self, widget, eve):
        widget.hide()

    def setPagerWidget(self):
        pager = wnck.Pager()
        self.builder.get_object('taskBarWorkspaces').add(pager)

    # ----        Screen Events        ----
    # NOTE: This is the worst way of doing this and kids die when these are run.
    #       We need to filter actions and more like add/remove buttons than just
    #       clearing everything. I'm sorry to all the families hurt by this....
    def activeWorkspaceChanged(self, screen, workspace):
        self.clearChildren(self.taskBarButtons)
        self.SCREEN = screen
        self.SCREEN.force_update() # (Re)populate screen windows list
        self.refreashTaskbar()

    def windowOpened(self, screen, window):
        self.SCREEN.force_update() # (Re)populate screen windows list
        btn = self.createWinBttn(window)
        self.setupSignals(btn, window)
        self.taskBarButtons.add(btn)

    def windowClosed(self, screen, window):
        self.clearChildren(self.taskBarButtons)
        self.SCREEN.force_update() # (Re)populate screen windows list
        self.refreashTaskbar()

    def clearChildren(self, parent):
        children = parent.get_children();
        for child in parent:
            child.destroy()

    # ----        Taskbar Button Events        ----
    def toggleMinimize(self, widget, data=None):
        if not self.window.is_minimized():
            self.window.minimize()
            widget.set_label("Unminimize")
        else:
            self.window.activate(1)
            widget.set_label("Minimize")

    def toggleMaximize(self, widget, data=None):
        if not self.window.is_maximized():
            self.window.maximize()
            widget.set_label("Unmaximize")
        else:
            self.window.unmaximize()
            widget.set_label("Maximize")

    def startMoveWindow(self, widget, data=None):
        self.window.keyboard_move()

    def startResizeWindow(self, widget, data=None):
        self.window.keyboard_size()

    def setTopState(self, widget):
        if not self.window.is_above():
            self.window.make_above()
        else:
            self.window.unmake_above()

    def setBelowState(self, widget):
        if not self.window.is_above():
            self.window.make_below()
        else:
            self.window.unmake_below()

    def setWorkspacePin(self, widget):
        if not self.window.is_pinned():
            self.window.pin()
        else:
            self.window.unpin()

    def closeAppWindow(self, widget, data=None):
        self.window.close(1)


        # WINDOW_SIGNALS
        # print(w.get_icon())
        # w.get_name()
        # w.get_icon()
        # w.get_mini_icon()
        # w.make_above()
        # w. pin()
        # w. get_state()  # https://lazka.github.io/pgi-docs/Wnck-3.0/flags.html#Wnck.WindowState
        # w.get_workspace()
        # w.set_workspace(workspace)
        # w.close()
        # w.is_above()
        # w.is_active()
        # w.is_below()
        # w.is_fullscreen()
        # w.is_maximized()
        # w.is_minimized()
        # w.is_pinned()
        # w.is_sticky()
