#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('conffile', nargs='?', default='TMVA.conf', help='TMVA config file')
optparser.add_argument('-l', dest='sglob', help='Session name glob for listing')
optparser.add_argument('-s', dest='session', default=None, help='Session name')
options = optparser.parse_args()
locals().update(_import_args(options))

import sys, os
if conffile and not os.path.exists(conffile):
    sys.exit('File not found: {}'.format(conffile))

from tmvaconfig import TMVAType, TMVAconfig, ConfigFile
conf = ConfigFile(conffile)
n = conf.read()

res = ''
valid_sessions = conf.sessions()
if sglob:                       # find requested session
    if reduce(lambda i,j: i or j, map(lambda x: x in sglob, '*?')): # glob
        from fnmatch import fnmatchcase
        for s in valid_sessions:
            if fnmatchcase(s, sglob): res = ' '.join([res, s])
    else:                           # exact
        if sglob in valid_sessions: res = ' '.join([res, sglob])
elif not session:               # print all sessions
    for s in valid_sessions: res = ' '.join([res, s])

if res:
    print '# sessions\n{}'.format(res)
    sys.exit(0)
