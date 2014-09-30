#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('conffile', nargs='?', default='TMVA.conf', help='TMVA config file')
optparser.add_argument('-s', dest='session', help='Session name (maybe glob)')
options = optparser.parse_args()
locals().update(_import_args(options))

import sys, os
if conffile and not os.path.exists(conffile):
    sys.exit('File not found: {}'.format(conffile))

from tmvaconfig import TMVAType, TMVAconfig, ConfigFile
conf = ConfigFile(conffile)
n = conf.read()

print '# sessions'
# print all sessions
if not session:
    for s in conf.sessions():
        print s,
    sys.exit(0)

# find requested session
if reduce(lambda i,j: i or j, map(lambda x: x in session, '*?')): # glob
    from fnmatch import fnmatchcase
    for s in conf.sessions():
        if fnmatchcase(s, session): print s,
else:                           # exact
    if session in conf.sessions():
        print session
