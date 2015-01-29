# coding=utf-8
"""Utilities"""

# argument parsing tools
from argparse import (ArgumentDefaultsHelpFormatter,
                      RawDescriptionHelpFormatter)
class RawArgDefaultFormatter(ArgumentDefaultsHelpFormatter,
                             RawDescriptionHelpFormatter):
    pass

def _import_args(namespace, d = {}):
    """Import attributes from namespace to local environment.

    namespace -- namespace to import attributes from
    d         -- dictionary that is returned with attributes
                 and values (default: empty dict, leave it
                 this way unless you know what you are doing)

    Usage:
      >>> opts = parser.parse_args(['foo', '-o', 'bar'])
      >>> locals().update(_import_args(opts))

    """
    attrs = vars(namespace)
    for attr in attrs:
        d[attr] = getattr(namespace, attr)
    return d

# plotting tools
def get_label(string):
    """Get label from variable names."""
    # NOTE: Do not remove leading/trailing spaces in replacement strings
    # special cases
    string = string.replace('lab345_MIN_PT', 'min D child trk p_{T}')
    string = string.replace('lab345_MIN_IPCHI2_OWNPV', 'min D child trk #chi^{2}')
    string = string.replace('lab1345_TRACK_GhostProb', 'max ghost trk prob')
    # LHCb tuple prefixes
    string = string.replace('lab0_', 'B ')
    string = string.replace('lab1_', 'bach ')
    string = string.replace('lab2_', 'D ')
    string = string.replace('lab3_', 'D child 1 ')
    string = string.replace('lab4_', 'D child 2 ')
    string = string.replace('lab5_', 'D child 3 ')
    # variables
    string = string.replace('_OWNPV', '')
    string = string.replace('PT', 'p_{T}')
    string = string.replace('MINIPCHI2', 'min IP #chi^{2}')
    string = string.replace('IPCHI2', 'IP #chi^{2}')
    string = string.replace('VCHI2NDOF', 'vtx #chi^{2}/ndof')
    string = string.replace('TAU', 'decay time')
    string = string.replace('ERR', ' error')
    return string

# ROOT -> rootpy tools
def hist_info(hist):
    """Return histogram info for using with rootpy"""
    metainfo = {'name': hist.GetName(), 'title': hist.GetTitle()}
    metainfo['type'] = hist.ClassName()[-1]
    dim = hist.GetDimension()
    # FIXME: only for 1D
    nbinsx = hist.GetNbinsX()
    axis = hist.GetXaxis()
    xmin = axis.GetXmin()
    xmax = axis.GetXmax()
    return (nbinsx, xmin, xmax), metainfo

def pycopy(newobj_t, obj_t, obj, *args, **kwargs):
    """Act as copy constructor for any object.

    Caution: nasty hack, use at your own peril

    """
    if isinstance(obj, obj_t):
        newobj = newobj_t(*args, **kwargs)
        newobj.__dict__.update(obj.__dict__)
    else:
        newobj = None
    return newobj

def th1fill(hist, dim=1):
    """Return a TH1.Fill wrapper for use with map(..)."""
    if 1 == dim:
        fill = lambda i: hist.Fill(i)
    elif 2 == dim:
        fill = lambda i, j: hist.Fill(i, j)
    elif 3 == dim:
        fill = lambda i, j, k: hist.Fill(i, j, k)
    else:
        fill = None
    return fill

# Generic range scanning tools
class Cut(object):
    """Cut object"""
    def __init__(self, val, var):
        self.val, self.var = val, var
        self.greater = '{}>{}'.format(var, val)
        self.greaterequal = '{}>={}'.format(var, val)
        self.lesser = '{}<{}'.format(var, val)
        self.lesserequal = '{}<={}'.format(var, val)

def crange(stops, var, tree):
    """Generator of cuts for a given list of stops"""
    for stop in stops:
        yield Cut(stop, var)

def scan_range(predicates, stops, var, tree):
    """Create cuts at stops, and run predicates over given tree.

       Returns the result in a nested list: [cut1_res, cut2_res, ...]
       Where, cutn_res: [res1, res2, ...]]

    """
    res = []
    for cut in crange(stops, var, tree):
        res.append(map(lambda fn: fn(tree, cut), predicates))
    return res

# I/O tools
def path2rootdir(path):
    """Read path string and return ROOT directory

    Returns (file/dir, directory)

    """
    from fixes import ROOT
    rfile, rdir = path.split(':', 1)
    rfile = ROOT.TFile.Open(rfile, 'read')
    rdir = rfile.GetDirectory(rdir) # path in root file: /foo/bar
    return (rfile, rdir)

def plot_conf(yamlfile, ftype, files):
    """Read plot config"""
    conf = read_yaml(yamlfile)
    if isinstance(conf, list):
        for entry in conf:
            if entry['file'] != ftype: continue
            rfiles = get_rpaths(files, entry)
    else:
        if conf['file'] == ftype:
            rfiles = get_rpaths(files, conf)
    return rfiles

def get_rpaths(files, conf):
    """Get ROOT file paths for all files using conf."""
    rfiles = []
    if isinstance(files, str): files = [files]
    from copy import deepcopy
    for rfile in files:
        copy = deepcopy(conf)
        copy.update(file = rfile)
        rfiles.append(make_paths(copy))
    return rfiles

def make_paths(node):
    """Return paths (directory) from dictionary

    This destroys the dictionary.  Make a deep copy if it needs to be
    reused.  See get_rpaths for an example.

    """
    try:
        pwd = node['name']
        del node['name']
    except KeyError:
        try:
            pwd = '{}:'.format(node['file'])
        except KeyError:
            print('Malformed dict')
            from pprint import pprint
            pprint(node)
            raise
    try:
        children = node['children']
        del node['children']
    except KeyError:
        children = None         # leaf node

    node.update(path = pwd)
    paths = [node]
    if children:
        for child in children:
            ret = make_paths(child)
            for i in ret:
                i['path'] = '{}/{}'.format(pwd, i['path'])
                paths.append(i)
    return paths

def read_yaml(filename):
    """Read yaml"""
    stream = open(filename, 'r')
    import yaml
    return yaml.load(stream)

def get_hists(yaml_keys, conf, tool, robj_t = None, robj_p = None):
    """Read histograms for `keys' for given `conf'

    conf is a list of dictionaries with rpaths.  The Rdir `tool' is
    used to read the histograms from the rpaths.

    """
    hists = {}
    for rdir in conf:
        try:
            if rdir['key'] in yaml_keys:
                hists.update({
                    rdir['key']:
                    tool.read(rdir['path'], robj_t = robj_t, robj_p = robj_p)
                })
        except KeyError as err:
            if str(err) != '\'key\'': raise
    return hists

# ROOT utils
def H1Dintegral(hist):
    """Return integral of 1D histogram (exclude overflow & underflow)"""
    integral = 0.0
    for bin in xrange(1, hist.GetNbinsX()+1):
        integral += hist.GetBinContent(bin) * hist.GetBinWidth(bin)
    return integral

def distance(hist, pt):
    """Calculate minimum distance from a given point"""
    dist = hist.GetXaxis().GetXmax()**2 + hist.GetYaxis().GetXmax()**2
    for bin in xrange(1, hist.GetNbinsX()+1):
        cpt = hist.GetBinCenter(bin), hist.GetBinContent(bin)
        dist_t = (cpt[0]-pt[0])**2 + (cpt[1]-pt[1])**2
        dist = dist_t if dist_t < dist else dist
    return dist

try:
    import numpy as np

    def thn2array(hist):
        """Convert ROOT histograms to numpy.array"""
        xbins = hist.GetNbinsX()
        ybins = hist.GetNbinsY()
        zbins = hist.GetNbinsZ()
        # add overflow, underflow bins
        if ybins == 1: shape = [xbins + 2]
        elif zbins == 1: shape = (xbins + 2, ybins + 2)
        else: shape = (xbins + 2, ybins + 2, zbins + 2)
        try:
            from fixes import ROOT
            from ROOT import TH1
            if isinstance(hist, TH1):
                val = np.array([val for val in hist]).reshape(*shape)
        except ImportError as err:
            val = np.array([val.value for val in hist]).reshape(*shape)
        return val

    def thn_print(hist):
        """Print ROOT histograms of any dimention"""
        val = thn2array(hist)
        print('Hist: {}, dim: {}'.format(hist.GetName(), len(np.shape(val))))
        hist.Print()
        print(np.flipud(val)) # flip y axis, FIXME: check what happens for 3D

except ImportError:
    import warnings
    # warnings.simplefilter('always')
    msg = 'Could not import numpy.\n'
    msg += 'Unavailable functions: thn2array, thn_print.'
    warnings.warn(msg, ImportWarning)

    def thn2array(hist):
        raise NotImplementedError('Not available without numpy')

    def thn_print(hist):
        raise NotImplementedError('Not available without numpy')
