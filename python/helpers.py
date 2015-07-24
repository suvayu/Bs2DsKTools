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


class FitStatus(object):
    """Fit status from Minuit"""
    fmt = '\033[3{};1mFit status: {} ({})\033[0m'

    def __init__(self, status):
        self.status = 'fail' if status else 'pass'
        self.code = status
        self.col = 1 if status else 2

    def __repr__(self):
        return self.fmt.format(self.col, self.status, self.code)


def suppress_warnings():
    """Suppress known annoying warnings"""
    # NOTE: This is to ignore a warning from the call to
    # TTreeFormula::EvalInstance().  One of the default arguments is a
    # char**.  PyROOT does not provide converters for that, leading to the
    # warning.  As long as this feature is not accessed, ignoring is safe.
    import warnings
    warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                            message='creating converter for unknown type.*')


def rf_msg_lvl(lvl, topic, obj):
    """Suppress RooFit logging"""
    from rplot.fixes import ROOT
    msgsvc = ROOT.RooMsgService.instance()
    for stream in xrange(msgsvc.numStreams()):
        if msgsvc.getStream(stream).match(lvl, topic, obj):
            msgsvc.setStreamStatus(stream, False)
