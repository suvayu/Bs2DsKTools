#!/usr/bin/python
# coding=utf-8
"""Exploratory script for ROOT files.

   Interactively explore a ROOT file with trees and histograms.  This
   script is meant to be run as `$ python -i <script.py>'

"""

import sys, os
from uuid import uuid4

from fixes import ROOT
from ROOT import gDirectory, gROOT, gSystem, gPad, gStyle
from ROOT import TFile, TTree, TH1D, TH2D, TH3D, TCanvas, TPad

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
    plottable_t = (ROOT.TH1, ROOT.TGraph, ROOT.TEfficiency)
    return isinstance(plottable, plottable_t)


# ROOT plotter
class Rplot(object):
    """Plotter class for ROOT"""

    colours = (kRed, kAzure, kGreen, kBlack, kPink, kOrange, kTeal,
               kCyan)

    markers = (kDot, kPlus, kStar, kCircle, kMultiply, kFullDotSmall,
               kFullDotMedium, kFullDotLarge, kFullCircle, kFullSquare,
               kFullTriangleUp, kFullTriangleDown, kOpenCircle,
               kOpenSquare, kOpenTriangleUp, kOpenTriangleDown)

    grid = (1,1)
    size = (400, 400)
    plottables = []
    style = True

    def __init__(self, xgrid, ygrid, width=None, height=None, style=None):
        self.grid = (xgrid, ygrid)
        self.nplots = xgrid * ygrid
        self.size = get_optimal_size(xgrid, ygrid, width, height)

    def prep_canvas(self):
        self.canvas = ROOT.TCanvas('canvas', '', self.size[0], self.size[1])
        if self.nplots > 1:
            self.canvas.Divide(*self.grid)

    def set_style(self, plottable, col):
        plottable.SetLineColor(self.colours[col] + 1)
        plottable.SetFillColor(self.colours[col])
        # plottable.SetMarker(self.markers)
        # plottable.SetMarkerSize(0.2)

    def draw_same(self, plottables, drawopts):
        for i, plottable in enumerate(plottables):
            if i == 0:
                opts = drawopts
            else:
                opts = '{} same'.format(drawopts)
            if self.style:
                self.set_style(plottable, i)
            plottable.Draw(opts)

    def draw_hist(self, plottables, drawopts):
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
