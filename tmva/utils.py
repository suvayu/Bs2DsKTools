# coding=utf-8
"""Utilities"""

# argument parsing tools
from argparse import (ArgumentDefaultsHelpFormatter,
                      RawDescriptionHelpFormatter)


class RawArgDefaultFormatter(ArgumentDefaultsHelpFormatter,
                             RawDescriptionHelpFormatter):
    pass


def _import_args(namespace, d={}):
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


def cacheobj(name, obj):
    import os
    import errno
    import pickle
    cachedir, cachefile = '.cache', '{}.pickle'.format(name)
    try:
        os.mkdir(cachedir)
    except OSError as err:
        if err.errno == errno.EEXIST:
            pass
    if obj:
        with open('{}/{}'.format(cachedir, cachefile), 'w') as cfile:
            pickle.dump(obj, cfile)
    elif os.path.exists('{}/{}'.format(cachedir, cachefile)):
        with open('{}/{}'.format(cachedir, cachefile), 'r') as cfile:
            return pickle.load(cfile)
    else:
        print 'No cached file: {}/{}'.format(cachedir, cachefile)


# ROOT utilities
def th1integral(hist):
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


# Generic range scanning tools
class Cut(object):
    """Cut object"""
    def __init__(self, val, var, plotvar):
        self.val, self.var, self.plotvar = val, var, plotvar
        self.greater = '{}>{}'.format(var, val)
        self.greaterequal = '{}>={}'.format(var, val)
        self.lesser = '{}<{}'.format(var, val)
        self.lesserequal = '{}<={}'.format(var, val)


def crange(stops, var, tree, plotvar):
    """Generator of cuts for a given list of stops"""
    for stop in stops:
        yield Cut(stop, var, plotvar)


def scan_range(predicates, stops, var, tree, plotvar=''):
    """Create cuts at stops, and run predicates over given tree.

       Returns the result in a nested list: [cut1_res, cut2_res, ...]
       Where, cutn_res: [res1, res2, ...]]

       When only one predicate is applied during the loop, simplify
       the output to return a simple list (no nesting).

    """
    from collections import Iterable
    if not isinstance(predicates, Iterable):
        predicates = [predicates]
    res = []
    for cut in crange(stops, var, tree, plotvar):
        res_i = map(lambda fn: fn(tree, cut), predicates)
        if len(res_i) == 1:
            res.append(res_i[0])
        else:
            res.append(res_i)
    return res


def make_varefffn(hist, refcut):
    """Return a function to pass to scan_range.

       The returned function does a histogram based efficiency
       calculation for given plotvar.

         cuts, plotvar → efficiency histograms

    """
    from rplot.utils import th1clonereset

    def efffn(tree, cut):
        hnumer = th1clonereset(hist, 'hnumer')
        hdenom = th1clonereset(hist, 'hdenom')
        heff = th1clonereset(hist, 'heff_{}_{}'.format(cut.plotvar, cut.val))
        tree.Draw('{}>>hnumer'.format(cut.plotvar),
                  '{}&&{}'.format(refcut, cut.greaterequal))
        tree.Draw('{}>>{}'.format(cut.plotvar, hdenom.GetName()), refcut)
        heff.Divide(hnumer, hdenom, 1, 1, 'B')
        return heff
    return efffn


# plotting tools
def colours(num, default=1):    # 1 == ROOT.kBlack
    from fixes import ROOT
    cols = [ROOT.kAzure, ROOT.kRed, ROOT.kGreen, ROOT.kBlack]
    try:
        return cols[num]
    except IndexError:
        return default


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
    metainfo['type'] = hist.ClassName()
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


# I/O tools
def path2rootdir(path):
    """Read path string and return ROOT directory

    Returns (file/dir, directory)

    """
    from fixes import ROOT
    rfile, rdir = path.split(':', 1)
    rfile = ROOT.TFile.Open(rfile, 'read')
    rdir = rfile.GetDirectory(rdir)  # path in root file: /foo/bar
    return (rfile, rdir)


def plot_conf(yamlfile, ftype, files):
    """Read plot config"""
    conf = read_yaml(yamlfile)
    if isinstance(conf, list):
        for entry in conf:
            if entry['file'] != ftype:
                continue
            rfiles = get_rpaths(files, entry)
    else:
        if conf['file'] == ftype:
            rfiles = get_rpaths(files, conf)
    return rfiles


def get_rpaths(files, conf):
    """Get ROOT file paths for all files using conf."""
    rfiles = []
    if isinstance(files, str):
        files = [files]
    from copy import deepcopy
    for rfile in files:
        copy = deepcopy(conf)
        copy.update(file=rfile)
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

    node.update(path=pwd)
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


def get_hists(yaml_keys, conf, tool, robj_t=None, robj_p=None):
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
                    tool.read(rdir['path'], robj_t=robj_t, robj_p=robj_p)
                })
        except KeyError as err:
            if str(err) != '\'key\'':
                raise
    return hists
