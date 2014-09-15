#!/usr/bin/python
# coding=utf-8
"""Plotting interface for ROOT objects"""

import sys, os
from uuid import uuid4

from fixes import ROOT
from ROOT import gROOT, gSystem, gDirectory, gPad, gStyle

# colours
from ROOT import (kBlack, kWhite, kGray, kViolet, kMagenta, kPink,
                  kRed, kOrange, kYellow, kSpring, kGreen, kTeal,
                  kCyan, kAzure, kBlue)

# markers
from ROOT import (kDot, kPlus, kStar, kCircle, kMultiply,
                  kFullDotSmall, kFullDotMedium, kFullDotLarge,
                  kFullCircle, kFullSquare, kFullTriangleUp,
                  kFullTriangleDown, kOpenCircle, kOpenSquare,
                  kOpenTriangleUp, kOpenTriangleDown)


# helpers
def get_screen_size():
    """Get screen size (linux only)"""
    import subprocess
    xrandr = subprocess.Popen(('xrandr', '-q'), stdout = subprocess.PIPE)
    displays = subprocess.check_output(('grep', '\*'), stdin = xrandr.stdout)
    displays = displays.splitlines()
    displays = [display.split()[0] for display in displays]
    displays = [display.split('x') for display in displays]
    displays = [(int(dim[0]), int(dim[1])) for dim in displays]
    xres = min(displays[0][0], displays[1][0])
    yres = min(displays[0][1], displays[1][1])
    return (xres - 50, yres - 50)

def get_optimal_size(xgrid, ygrid, width=None, height=None, aspect=4.0/3):
    """Calculate canvas size from grid"""
    _width = lambda h: int(float(h/ygrid) * aspect * xgrid)
    _height = lambda w: int(float(w/xgrid) * (1/aspect) * ygrid)
    if not (width or height):
        width, height = get_screen_size()
        if xgrid > ygrid:       # wide
            height = _height(width)
        elif ygrid > xgrid:     # tall
            width = _width(height)
        else:                   # square (xgrid == ygrid)
            width = height
    elif not width and height:  # get width
        width = _width(height)
    elif not height and width:  # get height
        height = _height(width)
    return (width, height)

def isplottable(plottable):
    plottable_t = (ROOT.TAttLine, ROOT.TAttFill, ROOT.TAttMarker,
                   ROOT.TAttText, ROOT.TAttBBox2D, ROOT.TAttImage)
    return isinstance(plottable, plottable_t)


# ROOT plotter
class Rplot(object):
    """Plotter class for ROOT"""

    fill_colours = (kRed, kAzure, kGreen, kGray+2, kMagenta, kOrange,
                    kTeal-9, kCyan-7)
    line_colours = (kRed+2, kAzure-6, kGreen+2, kBlack, kMagenta+2,
                    kOrange+1, kTeal-8, kCyan+1)

    markers = (kDot, kFullDotSmall, kCircle, kFullTriangleDown,
               kFullTriangleUp, kFullCircle, kPlus, kStar, kMultiply,
               kFullDotMedium, kFullDotLarge, kFullSquare,
               kOpenCircle, kOpenSquare, kOpenTriangleUp,
               kOpenTriangleDown)

    linestyles = {'-':1, '--':2, ':':3, '-.':5}

    grid = (1,1)
    size = (400, 400)
    plottables = []
    canvas = None
    style = True
    stats = False

    def __init__(self, xgrid, ygrid, width=None, height=None, style=None):
        if gROOT.IsBatch() and width and height:
            raise ValueError('Width and height specs are compulsory in batch mode!')
        self.grid = (xgrid, ygrid)
        self.nplots = xgrid * ygrid
        self.size = get_optimal_size(xgrid, ygrid, width, height)

    def prep_canvas(self):
        self.canvas = ROOT.TCanvas('canvas', '', *self.size)
        if self.nplots > 1:
            self.canvas.Divide(*self.grid)
        return self.canvas

    def set_style(self, plottable, num):
        if isinstance(plottable, ROOT.TAttFill):
            plottable.SetFillColorAlpha(self.fill_colours[num], 1-num*0.05)
        if isinstance(plottable, ROOT.TAttLine):
            plottable.SetLineColor(self.line_colours[num])
        if isinstance(plottable, ROOT.TH1):
            plottable.SetStats(self.stats)
        if isinstance(plottable, ROOT.TAttMarker):
            plottable.SetMarkerSize(0.2)
            plottable.SetMarkerStyle(self.markers[num])
            plottable.SetMarkerColor(self.line_colours[num])

    def get_viewport(self, plottables):
        ymin, ymax = 0, 0
        for plottable in plottables:
            ymin = min(ymin, plottable.GetMinimum())
            ymax = max(ymax, plottable.GetMaximum())
        if ymin < 0:
            ymin += 0.03*ymin
        if ymax > 0:
            ymax += 0.03*ymax
        return (ymin, ymax)

    def draw_same(self, plottables, drawopts):
        yrange = self.get_viewport(plottables)
        for i, plottable in enumerate(plottables):
            plottable.SetMinimum(yrange[0])
            plottable.SetMaximum(yrange[1])
            if i == 0:
                opts = drawopts
            else:
                opts = '{} same'.format(drawopts)
            if self.style:
                self.set_style(plottable, i)
            plottable.Draw(opts)

    def draw_hist(self, plottables, drawopts):
        if not self.canvas:
            self.prep_canvas()
        if len(plottables) % self.nplots == 0:
            for i, plot in enumerate(plottables):
                self.canvas.cd(i+1)
                if isplottable(plot):
                    if self.style:
                        self.set_style(plot, 0)
                    plot.Draw(drawopts)
                else:
                    self.draw_same(plot, drawopts)
        else:
            print(u'# plottables ({}) ≠ # pads ({})!'
                  .format(len(plottables), self.nplots))

    def draw_graph(self, *args, **kwargs):
        """Same as draw_hist(..)."""
        self.draw_hist(*args, **kwargs)

    def draw_tree(self, trees, exprs):
        if len(exprs) % len(trees) == 0:
            pass
