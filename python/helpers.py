# coding=utf-8

"""This module implements several helper tools.

"""


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
    import re
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


def rf_fr_ytitle(fr):
    import re
    re.IGNORECASE = True
    try:
        units = re.findall('\[[a-z]+\]', fr.GetXaxis().GetTitle())[-1]
    except IndexError:          # no units found in axis title
        units = ''
    fr.GetYaxis().SetTitle('candidates / {bw} {unit}'.format(
        bw=fr.getFitRangeBinW(), unit=units))
    return fr


def rf_fr_style(fr, xtitle=None, ytitle=None):
    fr.SetTitle('')
    # fr.SetAxisRange(0, 1.05*fr.GetMaximum(), 'Y')
    if isinstance(xtitle, str):
        fr.GetXaxis().SetTitle(xtitle)
    if isinstance(ytitle, str):
        fr.GetYaxis().SetTitle(ytitle)
    else:
        rf_fr_ytitle(fr)
    return fr


def plot_diff_canvas(sz=(1024, 640), frac=0.25):
    import uuid
    from rplot.fixes import ROOT
    canvas = ROOT.TCanvas('c_{}'.format(uuid.uuid4()), '', 1024, 640+210)  # FIXME: calc
    canvas.SetRightMargin(0.1)
    canvas.cd()
    plot = ROOT.TPad('p_{}'.format(uuid.uuid4()), '', 0.0, frac, 1.0, 1.0)
    plot.SetBottomMargin(0.1)
    diff = ROOT.TPad('p_{}'.format(uuid.uuid4()), '', 0.0, 0.0, 1.0, frac)
    diff.SetTopMargin(0.0)
    diff.SetBottomMargin(0.15)
    plot.Draw()
    diff.Draw()
    return plot, diff, canvas


def diff_axis_style(axis, divs):
    axis.SetNdivisions(divs)
    axis.SetLabelSize(0.1)
