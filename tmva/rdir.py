#coding=utf-8
"""A global filesystem-like hierarchy of ROOT objects in PyROOT

"""

import os.path

class pathspec(object):
    """Path specification as expected by ROOT.

    Paths inside the current file can be specified in the usual way:
    - full path: /dir1/dir2
    - relative path: ../dir1

    Paths in other root files have to be preceded by the file name and
    a colon:
    - file path: myfile.root:/dir1/dir2

    See: TDirectoryFile::cd(..) in ROOT docs

    Useful information is provided as properties.

    Example:
    >>> ps = pathspec('foo.root:/path/to/obj/bar')
    >>> if ps.relative:
    ...     obj = rfile.Get(ps.rpath)
    ... else:
    ...     rfile = TFile.Open(ps.rfile, 'read')
    ...     obj = rfile.Get(ps.rpath)

    """
    # declare properties for pydoc
    rfile, rpath = None, None
    norfile, norpath = None, None
    relative = None
    rfile_basename, rfile_dirname, rfile_split = None, None, None
    rpath_basename, rpath_dirname, rpath_split = None, None, None
    

    def __init__(self, path):
        if path.find(':') < 0:
            if path.find('.root') < 0:
                self.rfile = ''
                self.rpath = path
            else:
                self.rfile = path
                self.rpath = ''
        else:
            self.rfile, self.rpath = path.split(':', 1)
        self.rpath = self.rpath.rstrip('/')
        self.norfile = not self.rfile
        self.norpath = not self.rpath
        self.relative = self.rpath.find('../') == 0 or \
                        self.rpath.find('/') > 0
        if self.rfile and self.relative:
            raise ValueError('Relative paths not allowed when a file is specified')

        # utilities
        self.rfile_dirname = os.path.dirname(self.rfile)
        self.rfile_basename = os.path.basename(self.rfile)
        self.rfile_split = os.path.split(self.rfile)
        self.rpath_split = os.path.split(self.rpath)
        self.rpath_basename = os.path.basename(self.rpath)
        self.rpath_dirname = os.path.dirname(self.rpath)
