"""Provides fixes and workarounds for many ROOT eccentricities.

It also adds methods to ROOT classes so that they support standard
Python API for common tasks (e.g. iteration), language constructs
(e.g. `if .. in ..:'), etc.

To use these fixes/features, one should import ROOT from this module
before doing anything.

  >>> from fixes import ROOT

@author Suvayu Ali
@email Suvayu dot Ali at cern dot ch
@date 2014-09-05 Fri

"""


import ROOT


## General helpers
def set_attribute(clss, attr, value):
    """For all cls in clss, set cls.attr to value.

    If value is a string, treat it is as an existing cls attribute and
    remap its value to attr (cls.attr = cls.value ).

    """
    def _setter(cls, attr, value):
        if isinstance(value, str):
            value = getattr(cls, value)
        setattr(cls, attr, value)
    try:
        for cls in clss:
            _setter(cls, attr, value)
    except TypeError:
        _setter(clss, attr, value)


## Ownership fixes
# list of creators
_creators = [
    ROOT.TObject.Clone,
    ROOT.TFile.Open,
]

def set_ownership(methods):
    """Tell Python, caller owns returned object by setting `clsmethod._creates'"""
    set_attribute(methods, '_creates', True)

set_ownership(_creators)


_root_containers = [
    ROOT.TCollection
]

# `if <item> in <container>:' construct
set_attribute(_root_containers, '__contains__', 'FindObject')
