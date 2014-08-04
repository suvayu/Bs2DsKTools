#!/usr/bin/python
# coding=utf-8
"""Exploratory script for ROOT files.

   Interactively explore a ROOT file with trees and histograms.  This
   script is meant to be run as `$ python -i <script.py>'

"""

import argparse

optparser = argparse.ArgumentParser(description=__doc__)
optparser.add_argument('filename', nargs='+', help='ROOT file')
options = optparser.parse_args()
filenames = options.filename

import sys, os
import subprocess
from uuid import uuid4

# history file for interactive use
import atexit, readline
history_path = '.browse.py'
def save_history(history_path=history_path):
    import readline
    readline.write_history_file(history_path)

if os.path.exists(history_path):
    readline.read_history_file(history_path)

atexit.register(save_history)
del atexit, readline, save_history, history_path


from ROOT import gDirectory, gROOT, gSystem, gPad, gStyle
from ROOT import TFile, TTree, TH1D, TH2D, TH3D, TCanvas, TPad

# colours
from ROOT import (kBlack, kWhite, kGray, kViolet, kMagenta, kPink,
                  kRed, kOrange, kYellow, kSpring, kGreen, kTeal,
                  kCyan, kAzure, kBlue)

_colours = (kBlack, kWhite, kGray, kViolet, kMagenta, kPink, kRed,
            kOrange, kYellow, kSpring, kGreen, kTeal, kCyan, kAzure,
            kBlue)
# markers
from ROOT import (kDot, kPlus, kStar, kCircle, kMultiply,
                  kFullDotSmall, kFullDotMedium, kFullDotLarge,
                  kFullCircle, kFullSquare, kFullTriangleUp,
                  kFullTriangleDown, kOpenCircle, kOpenSquare,
                  kOpenTriangleUp, kOpenTriangleDown)

_markers = (kDot, kPlus, kStar, kCircle, kMultiply, kFullDotSmall,
            kFullDotMedium, kFullDotLarge, kFullCircle, kFullSquare,
            kFullTriangleUp, kFullTriangleDown, kOpenCircle,
            kOpenSquare, kOpenTriangleUp, kOpenTriangleDown)

# ownership
TFile.Open._creates = True

rfiles = []
for f in filenames:
    rfiles.append(TFile.Open(filename))
if not rfiles:
    sys.exit('Did you forget to provide a file to browse?')


def ls(directory = gDirectory):
    """List contents of present or specified directory."""
    if isinstance(directory, str):
        directory = gDirectory.GetDirectory(directory)
    directory.ls()


def cd(directory):
    """Change directory"""
    gDirectory.cd(directory)


def cd(dirname):
    """Change directory to specified directory."""
    return gDirectory.cd(dirname)


def read(name, newname = ''):
    """Read the object with given name (paths allowed)."""
    # with_path = name.find('/')
    if len(newname):
        return gDirectory.Get(name).Clone(newname)
    else:
        return gDirectory.Get(name)


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


def _screen_size():
    """Get screen size (linux only)"""
    xrandr = subprocess.Popen(('xrandr', '-q'), stdout = subprocess.PIPE)
    displays = subprocess.check_output(('grep', '\*'), stdin = xrandr.stdout)
    displays = displays.splitlines()
    displays = [display.split()[0] for display in displays]
    displays = [display.split('x') for display in displays]
    displays = [(int(dim[0]), int(dim[1])) for dim in displays]
    xres = min(displays[0][0], displays[1][0])
    yres = min(displays[0][1], displays[1][1])
    return (xres - 50, yres - 50)


def _canvas_size(grid):
    """Calculate canvas size from grid"""
    nplots = grid[0]*grid[1]
    xmax, ymax = _screen_size()
    wide = grid[0] > grid[1]
    tall = grid[1] > grid[0]
    if wide == tall:            # square
        return (ymax, ymax)
    if wide:
        y = int(float(xmax/grid[0]) * 0.75 * grid[1])
        return (xmax, y)
    if tall:
        x = int(float(ymax/grid[1]) * 1.33 * grid[0])
        return (x, ymax)


def _check_cols(cols, nhists):
    """Check colours"""
    if cols:
        _assert_equal(len(cols), nhists, '# colours', '# histograms')
    else:
        cols = [kBlack] * nhists
    return cols


def draw(plottables, scheme = None, grid = (1,1), cols = None):
    """Draw histograms"""
    cols = _check_cols(cols, len(plottables))
    scheme = _valid_scheme(scheme, len(plottables), grid)
    if not scheme: return

    size = _canvas_size(grid)
    canvas = TCanvas('canvas-{}'.format(uuid4()), '', size[0], size[1])
    canvas.Divide(grid[0], grid[1])
    pad = 0
    for idx, plottable in enumerate(plottables):
        if scheme[idx].find('same') < 0:
            pad = pad + 1
        canvas.cd(pad)
        plottable.Draw(scheme[idx])
        plottable.SetLineColor(cols[idx])
        plottable.SetMarkerColor(cols[idx])
    canvas.Update()
    return canvas


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
