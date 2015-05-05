#!/usr/bin/env python

import argparse
from utils import RawArgDefaultFormatter, is_match

optparser = argparse.ArgumentParser(formatter_class=RawArgDefaultFormatter,
                                    description=__doc__)
optparser.add_argument('sessions', nargs='+',  help='Session names (or globs)')
optparser.add_argument('--conf', default='TMVA.conf', help='TMVA config file')
optparser.add_argument('--nvars', action='store_true', default=False,
                       help='Normal variables')
optparser.add_argument('--cvars', action='store_true', default=False,
                       help='Combined variables')
group = optparser.add_mutually_exclusive_group()
group.add_argument('--cuts_both', action='store_true', default=False,
                   help='Cuts common to both signal & background')
group.add_argument('--cuts_bkg', action='store_true', help='Background only cuts')
group.add_argument('--cuts_sig', action='store_true', help='Signal only cuts')
opts = optparser.parse_args()

import sys
import os
if not os.path.exists(opts.conf):
    sys.exit('File not found: {}'.format(opts.conf))

from tmvaconfig import ConfigFile
conf = ConfigFile(opts.conf)
n = conf.read()

# filter out when not a match or invalid
sessions = filter(lambda s: is_match(s, opts.sessions), conf.sessions())

res = ' '.join(sessions)
if res:
    print res

if not (opts.cvars or opts.nvars or opts.cuts_both or opts.cuts_sig
        or opts.cuts_bkg):
    sys.exit(0)

# helper
one_per_line = lambda i: '\n'.join(i)

for session in sessions:
    config = conf.get_session_config(session)
    print '\n{}:'.format(config._name)
    if opts.nvars:
        print one_per_line(config.vars)
    if opts.cvars:
        print one_per_line(config.combined_vars)
    if opts.cuts_both:
        print config.cut_both
    if opts.cuts_sig:
        print config.cut_sig
    if opts.cuts_bkg:
        print config.cut_bkg
