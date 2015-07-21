# coding=utf-8
"""Some plotting utilities"""


def get_limits(hist, xaxis=True):
    """Get limits of histogram"""
    if xaxis:
        return (hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    else:
        return (hist.GetMinimum(), hist.GetMaximum())


def get_mark(hist, mark, yaxis):
    """Get an axis that marks the histogram"""
    from rplot.fixes import ROOT
    limits = get_limits(hist, xaxis=yaxis)
    if yaxis:
        return ROOT.TGaxis(limits[0], mark, limits[1], mark, 0, 0, 0)
    else:
        return ROOT.TGaxis(mark, limits[0], mark, 1.05*limits[1], 0, 0, 0)


def get_arrow(mark, arrow, yaxis, sz, opt):
    """Get an arrow at mark"""
    from rplot.fixes import ROOT
    if yaxis:
        return ROOT.TArrow(arrow[0], mark, arrow[0], arrow[1], sz, opt)
    else:
        return ROOT.TArrow(mark, arrow[1], arrow[0], arrow[1], sz, opt)
