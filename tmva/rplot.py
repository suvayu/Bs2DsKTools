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


def _assert_equal(arg1, arg2, str1, str2):
    """Assert the args are equal, raise exception otherwise"""
    if arg1 != arg2:
        raise ValueError('Value mismatch: {} != {}'.format(str1, str2))


def _valid_scheme(scheme, nplots, grid):
    """Check plotting scheme"""
    if len(grid) != 2:
        raise ValueError('Invalid grid dimensions, expected form: (x,y).')
    npads = grid[0]*grid[1]
    if not scheme:
        _assert_equal(npads, nplots, 'grid size', '# of plottables')
        scheme = [''] * nplots
    else:
        if scheme[0].find('same') >= 0:
            raise ValueError('First plotting scheme has `same\'!  This is not allowed.')
        _assert_equal(npads, len([True for opt in scheme if opt.find('same') < 0]),
                      '# of plots', 'plotting scheme')
    return scheme


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


def draw_expr(trees, exprs, scheme = None, grid = (1,1), sel = '', cols = None):
    """Draw expressions from trees"""
    nhists = len(exprs)
    _assert_equal(len(trees), nhists, '# trees', '# expressions')
    if isinstance(sel, str):
        sel = [sel] * nhists
    else:
        _assert_equal(len(sel), nhists, '# selections', '# expressions')
    _check_cols(cols, nhists)
    scheme = _valid_scheme(scheme, nhists, grid)

    size = _canvas_size(grid)
    canvas = TCanvas('canvas-{}'.format(uuid4()), '', size[0], size[1])
    canvas.Divide(grid[0], grid[1])
    pad = 0
    for idx, tree in enumerate(trees):
        if scheme[idx].find('same') < 0:
            pad = pad + 1
        canvas.cd(pad)
        hname = 'hist-{}'.format(uuid4())
        expr = '{}>>{}'.format(exprs[idx], hname)
        print 'Drawing: {}'.format(expr)
        tree.Draw(expr, sel[idx], scheme[idx])
        hist = gROOT.FindObject(hname)
        hist.SetLineColor(cols[idx])
        hist.SetMarkerColor(cols[idx])
    canvas.Update()
    return canvas


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
        self.canvas = ROOT.Canvas('canvas', '', *self.size)
        if self.nplots > 1:
            self.canvas.Divide(*self.grid)

    def draw_hist(self, plottables, drawopts):
        if len(plottables) % self.nplots == 0:
            for i, plot in enumerate(plottables):
                this_plot = i % self.nplots
                if this_plot == 0:
                    self.canvas.cd(i/self.nplots + 1)
                    opts = drawopts
                else:
                    opts = '{} same'.format(drawopts)
                if self.style:
                    plottables.SetLineColor(self.colours[this_plot] + 1)
                    plottables.SetFillColor(self.colours[this_plot])
                    plottables.SetMarker(self.markers)
                    plottables.SetMarkerSize(0.2)
                plottables.Draw(opts)
        else:
            print(u'# plottables ({}) ≠ # pads ({})!'
                  .format(len(plottables), self.nplots))

    def draw_graph(self, *args, **kwargs):
        """Same as draw_hist(..)."""
        self.draw_hist(*args, **kwargs)

    def draw_tree(self, trees, exprs):
        if len(exprs) % len(trees) == 0:
            pass
