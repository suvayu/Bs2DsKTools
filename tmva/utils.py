# coding=utf-8
"""Utilities"""

# pretty print
from pprint import pprint

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

def make_paths(node):
    """Return paths (directory) from dictionary"""
    try:
        pwd = node['name']
    except KeyError:
        print 'Malformed dict'
        pprint(node)
        raise
    try:
        children = node['children']
    except KeyError:
        children = None         # leaf node

    paths = [pwd]
    if children:
        for child in children:
            ret = make_paths(child)
            for i in ret:
                paths.append('{}/{}'.format(pwd, i))
    return paths

def read_yaml(filename):
    """Read yaml"""
    stream = open(filename, 'r')
    import yaml
    return yaml.load(stream)
