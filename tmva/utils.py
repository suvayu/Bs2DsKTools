# coding=utf-8
"""Utilities"""

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

def path2rootdir(path):
    """Read path string and return ROOT directory

    Returns (file/dir, directory)

    """
    from fixes import ROOT
    rfile, rdir = path.split(':', 1)
    rfile = ROOT.TFile.Open(rfile, 'read')
    rdir = rfile.GetDirectory(rdir) # path in root file: /foo/bar
    return (rfile, rdir)

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
            print 'Malformed dict'
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
    """Read histograms for `keys' for given `conf'"""
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
    val = np.array([val for val in hist]).reshape(*shape)
    return val

def thn_print(hist):
    """Print ROOT histograms of any dimention"""
    val = thn2array(hist)
    print('Hist: {}, dim: {}'.format(hist.GetName(), len(np.shape(val))))
    hist.Print()
    print np.flipud(val) # flip y axis, FIXME: check what happens for 3D
