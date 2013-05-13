# coding=utf-8

"""This module implements several helper tools.

"""

import re

def sanitise_str(string, splchars=True):
    "Sanitise string for use as labels or filenames (as per flag)."

    # NOTE: Do not remove leading spaces in replacement strings
    if splchars:
        string = string.replace('_', ' ')
        # LHCb tuple prefixes
        string = string.replace('CHI2', ' #chi^{2}')
    else:
        string = sanitise_str_src(string)

    # LHCb tuple prefixes
    string = string.replace('lab0', 'B')
    string = string.replace('lab1', 'bach')
    string = string.replace('TAU', 'decay time')
    string = string.replace('ERR', ' error')
    return string


def sanitise_str_src(string):
    "Sanitise strings for use in names in source code."

    return re.sub('[-%.+*?=()\[\]{} ^]', '_', string)
