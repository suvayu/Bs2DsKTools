#!/usr/bin/env python

import argparse
from utils import _import_args

optparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                    description=__doc__)
optparser.add_argument('conffile', nargs='?', default='TMVA.conf', help='TMVA config file')
optparser.add_argument('-l', dest='sglob', help='Session name glob for listing')
optparser.add_argument('-s', dest='session', default=None, help='Session name')
optparser.add_argument('--nvars', action='store_true', default=False, help='Normal variables')
optparser.add_argument('--cvars', action='store_true', default=False, help='Combined variables')
group = optparser.add_mutually_exclusive_group()
group.add_argument('--cuts_both', action='store_true', default=False, help='Common cuts')
group.add_argument('--cuts_bkg', action='store_true', default=False, help='Background only cuts')
group.add_argument('--cuts_sig', action='store_true', default=False, help='Signal only cuts')
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

## list sessions
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

# helper
one_per_line = lambda i: '\n'.join(i)

## list session specifics
assert(session)
if session in valid_sessions:
    config = conf.get_session_config(session)
    if nvars: res = one_per_line(config.vars)
    if cvars:
        if res: res += '\n'
        res += one_per_line(config.combined_vars)
    if cuts_both: res = config.cut_both
    if cuts_sig: res = config.cut_sig
    if cuts_bkg: res = config.cut_bkg
else:
    sys.exit('Could not find session')

if res:
    print '# session: {}'.format(session)
    print res
    sys.exit(0)
