import sys
import math

class RunningAverage(object):

    def __init__(self, ):
        self.__mean__ = 0.
        self.__var__ = 0.
        self.__min__ = sys.float_info.max
        self.__max__ = sys.float_info.min
        self.__nentries__ = 0

    def reset(self):
        self.__mean__ = 0.
        self.__var__ = 0.
        self.__min__ = sys.float_info.max
        self.__max__ = sys.float_info.min
        self.__nentries__ = 0

    def fill(self, x):
        """Calculate running average and variance."""
        self.__nentries__ += 1
        if x == self.__mean__ and 0. == self.__var__: return
        newmean = self.__mean__ + (x - self.__mean__) / self.__nentries__
        # Both ways of calculating variance is correct.  The first
        # one, uses associativity and other properties of expectation
        # values, whereas the second uses recursion relations
        newvar = self.__var__ - (newmean - self.__mean__) * (newmean - self.__mean__) + (
            (x - self.__mean__) * (x - self.__mean__) - self.__var__) / self.__nentries__
        # newvar = (x**2 + (self.__nentries__ - 1) * (
        #     self.__var__ + self.__mean__**2)) / self.__nentries__ - newmean**2
        self.__mean__ = newmean
        self.__var__ = newvar
        if (self.__min__ > x): self.__min__ = x
        if (self.__max__ < x): self.__max__ = x
        return

    def entries(self):
        return self.__nentries__

    def mean(self):
        return self.__mean__

    def var(self):
        return self.__var__

    def rms(self):
        return math.sqrt(self.__var__)

    def min(self):
        return self.__min__

    def max(self):
        return self.__max__
