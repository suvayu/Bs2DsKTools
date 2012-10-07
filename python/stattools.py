# coding=utf-8

"""This module implements several statistical tools.

Classes: RunningAverage, BinnedAvgFunction

"""

import sys
import math

class RunningAverage(object):
    """This class calculates running means and variances.

    There are two methods to do this; the default uses associativity
    and other properties of expectation values for the calculation
    whereas the alternate method uses recursion relations.

    """

    def __init__(self):
        self.__mean__ = 0.
        self.__var__ = 0.
        self.__min__ = sys.float_info.max
        self.__max__ = sys.float_info.min
        self.__nentries__ = 0

    def reset(self):
        """Reset running average calculation."""
        self.__init__()

    def fill(self, x):
        """Calculate running average and variance (default method).

        Both ways of calculating variance is correct.  The default
        method uses associativity and other properties of expectation
        values, whereas the alternate uses recursion relations

        """

        self.__nentries__ += 1
        if x == self.__mean__ and 0. == self.__var__: return
        newmean = self.__mean__ + (x - self.__mean__) / self.__nentries__
        newvar = self.__var__ - (newmean - self.__mean__) * (newmean - self.__mean__) + (
            (x - self.__mean__) * (x - self.__mean__) - self.__var__) / self.__nentries__
        # newvar = (x**2 + (self.__nentries__ - 1) * (
        #     self.__var__ + self.__mean__**2)) / self.__nentries__ - newmean**2
        self.__mean__ = newmean
        self.__var__ = newvar
        if (self.__min__ > x): self.__min__ = x
        if (self.__max__ < x): self.__max__ = x
        return

    def alt_fill(self, x):
        """Calculate running average and variance (alternate method).

        Both ways of calculating variance is correct.  The default
        method uses associativity and other properties of expectation
        values, whereas the alternate uses recursion relations

        """

        self.__nentries__ += 1
        if x == self.__mean__ and 0. == self.__var__: return
        newmean = self.__mean__ + (x - self.__mean__) / self.__nentries__
        # newvar = self.__var__ - (newmean - self.__mean__) * (newmean - self.__mean__) + (
        #     (x - self.__mean__) * (x - self.__mean__) - self.__var__) / self.__nentries__
        newvar = (x**2 + (self.__nentries__ - 1) * (
            self.__var__ + self.__mean__**2)) / self.__nentries__ - newmean**2
        self.__mean__ = newmean
        self.__var__ = newvar
        if (self.__min__ > x): self.__min__ = x
        if (self.__max__ < x): self.__max__ = x
        return

    def entries(self):
        """Return number of filled entries."""
        return self.__nentries__

    def mean(self):
        """Return mean."""
        return self.__mean__

    def var(self):
        """Return variance."""
        return self.__var__

    def rms(self):
        """Return RMS or sqrt(varaiance)."""
        return math.sqrt(self.__var__)

    def min(self):
        """Return minimum."""
        return self.__min__

    def max(self):
        """Return maximum."""
        return self.__max__


import numpy
from ROOT import TF1

class BinnedAvgFunction(object):
    """Finds binned average of an ensemble of ROOT functions.

    The running average of the ensemble of ROOT functions in bins are
    used as the binned average function.  The running variances of the
    ensemble are treated as vertical error bars for the function.

    """

    def __init__(self, fnlist, xbins):
        self.__fns__ = fnlist
        self.__xbins__ = xbins
        self.__fnavg__ = numpy.zeros(len(xbins), dtype=float)
        self.__fnavgerr__ = numpy.zeros(len(xbins), dtype=float)

    def calculate(self):
        """Calculate average and variances."""
        for i, xval in enumerate(self.__xbins__):
            ravg = RunningAverage()
            for fn in self.__fns__:
                ravg.fill(fn.Eval(xval))
            self.__fnavg__[i] = ravg.mean()
            self.__fnavgerr__[i] = ravg.rms()

    def get_avg_fn(self):
        """Return binned average function."""
        return self.__fnavg__

    def get_avg_fn_var(self):
        """Return variance for binned average function."""
        return self.__fnavgerr__
