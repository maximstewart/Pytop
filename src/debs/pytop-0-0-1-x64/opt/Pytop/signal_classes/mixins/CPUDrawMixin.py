#!/usr/bin/python3


# Python Imports
from __future__ import division
import cairo, psutil


# GTK Imports
from gi.repository import GObject
from gi.repository import GLib





class CPUDrawMixin:
    # Note: y-axis on draw area goes from top to bottom when increasing.
    # Need to do the math such that you subtract from max height to start from bottom to go up
    # self.linePoints.append([1 * xStep, ah - (23 * yStep)]) # 23%
    # self.linePoints.append([2 * xStep, ah - (60 * yStep)]) # 60%
    # self.drawPointLine()
    # del self.linePoints[0:1]
    # self.linePoints.append([3 * xStep, ah - (44 * yStep)]) # 44%
    def updateCPUPoints(self):
        # Clears screen when enough points exist and unshifts the
        # first point to keep fixed range
        self.drawBackground(self.brush, self.aw, self.ah)
        del self.cpu_percents[0:1]

        precent = psutil.cpu_percent()
        self.cpu_percents.append(precent)
        self.drawPointLine() # Will re-draw every point
        self.drawArea.queue_draw()

        return True


    def drawPointLine(self):
        self.brush.set_line_width(self.brushSizeVal)
        self.brush.set_line_cap(1) # 0 = BUTT, 1 = ROUND, 2 = SQUARE

        oldX = 0.0
        oldP = 0.0
        i    = 1
        for p in self.cpu_percents:
            # set color depending on usage...
            rgba = self.brushColorVal
            if p > 50.0:
                rgba = self.warning
            if p > 85.0:
                rgba = self.danger

            self.brush.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])

            # Movbe to prev. point if any
            if oldP is not 0.0 and oldX is not 0.0:
                x  = oldX
                y  = float(self.ah) - (oldP * self.yStep)
                self.brush.move_to(x, y)

            # Draw line to the new point from old point
            x2 = i * self.xStep
            y2 = float(self.ah) - (p * self.yStep)
            self.brush.line_to(x2, y2)
            self.brush.stroke()

            # Collect info to use as prev. pint
            oldX = x2
            oldP = p
            i    += 1


    def onConfigure(self, area, eve, data = None):
        aw           = area.get_allocated_width()
        ah           = area.get_allocated_height()
        self.aw      = aw
        self.ah      = ah
        self.xStep   = aw / 200  # For x-axis
        self.yStep   = ah / 100 # For y-axis %s
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, aw, ah)
        self.brush   = cairo.Context(self.surface)

        self.drawBackground(self.brush, aw, ah)
        if not self.isDrawing:
            self.fillCPUPercents()
            self.startCPUGraph()
            self.isDrawing = True

        return False

    # Fill with y bank with 50%s
    def fillCPUPercents(self):
        self.cpu_percents = [50.0] * 198


    # Draw background white
    def drawBackground(self, brush, aw, ah):
        brush.rectangle(0, 0, aw, ah) # x, y, width, height
        brush.set_source_rgba(1, 1, 1, 1.0) # x, y, width, height

        if not self.doDrawBackground: # If transparent or white
            self.brush.set_operator(0);

        brush.fill()
        self.brush.set_operator(1); # reset the brush after filling bg...


    # Starting graph generation
    def startCPUGraph(self):
        GObject.timeout_add(self.updateSpeed, self.updateCPUPoints)


    def onDraw(self, area, brush):
        if self.surface is not None:
            brush.set_source_surface(self.surface, 0.0, 0.0)
            brush.paint()
        else:
            print("No surface info...")

        return False


    def onColorSet(self, widget):
        rgba = widget.get_rgba()
        self.brushColorVal = [rgba.red, rgba.green, rgba.blue, rgba.alpha]

    def onBrushSizeChange(self, widget):
        self.brushSizeVal = self.brushSizeProp.get_value()
