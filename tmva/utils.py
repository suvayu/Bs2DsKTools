# coding=utf-8
"""Utilities"""

# pretty print
from pprint import pprint
import ROOT

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

def path2rootdir(path, ext='.root'):
    """Read path string and return ROOT directory

    Returns (file/dir, directory)

    """
    res = path.split(ext, 1)
    rfile = ROOT.TFile.Open('{}{}'.format(res[0], ext), 'read')
    rdir = rfile.GetDirectory(res[-1]) # path in root file: /foo/bar
    return (rfile, rdir)

def make_paths(node):
    """Return paths (directory) from dictionary"""
    try:
        pwd = node['name']
        del node['name']
    except KeyError:
        print 'Malformed dict'
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
