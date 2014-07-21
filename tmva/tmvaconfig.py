#!/usr/bin/env python

import sys, os

# Config script for TMVA Classification and Application
# _varlist entries have format [varname_in_tree, name, unit, type]
# _combvarlist entries have format [vareval_in_c, name, unit, type, vareval_in_python]
# _branchmask is renaming the branches from the signal tree in the classification, in case the branch names don't match

from collections import Iterable


class TMVAconfig(object):
   """Config class for TMVA Classification and Application"""

   def __init__(self, name):
      self._name = name
      self._cut_sig = ''
      self._cut_bkg = ''

   @property
   def vars(self):
      """Normal training MVA variables"""
      return self._vars

   @vars.setter
   def vars(self, value):
      if isinstance(value, Iterable):
         self._vars = value
      else:
         raise ValueError('Expecting an iterable')

   @vars.deleter
   def vars(self):
      del self._vars

   @property
   def combined_vars(self):
      """Combined training MVA variables"""
      return self._combined_vars

   @combined_vars.setter
   def combined_vars(self, value):
      if isinstance(value, Iterable):
         self._combined_vars = value
      else:
         raise ValueError('Expecting an iterable')
   
   @combined_vars.deleter
   def combined_vars(self):
      del self._combined_vars
   
   def all_vars(self):
      return self._vars + self._combined_vars

   @property
   def spectators(self):
      """Spectator variables (not trained)"""
      return self._spectators

   @spectators.setter
   def spectators(self, value):
      if isinstance(value, Iterable):
         self._spectators = value
      else:
         raise ValueError('Expecting an iterable')

   @spectators.deleter
   def spectators(self):
      del self._spectators

   @property
   def cut_sig(self):
      """Cuts on signal sample"""
      return self._cut_sig

   @cut_sig.setter
   def cut_sig(self, value) :
      if isinstance(value, str) or isinstance(value, TCut):
         self._cut_sig = value
      else:
         raise ValueError('Expecting a cut string or TCut')

   @cut_sig.deleter
   def cut_sig(self):
      del self._cut_sig

   @property
   def cut_bkg(self):
      """Cuts on background sample"""
      return self._cut_bkg

   @cut_bkg.setter
   def cut_bkg(self, value) :
      if isinstance(value, str) or isinstance(value, TCut):
         self._cut_bkg = value
      else:
         raise ValueError('Expecting a cut string or TCut')

   @cut_bkg.deleter
   def cut_bkg(self):
      del self._cut_bkg

   @property
   def branch_mappings(self):
      """Input tree branch name mappings"""
      return self._branch_mappings

   @branch_mappings.setter
   def branch_mappings(self, value) :
      if isinstance(value, Iterable):
         self._branch_mappings = value
      else:
         raise ValueError('Expecting an iterable')

   @branch_mappings.deleter
   def branch_mappings(self):
      del self._branch_mappings


from ConfigParser import ConfigParser, ParsingError
from ROOT import TCut


class ConfigFile(object):
   """Read/write TMVA configuration from/to a file"""
   def __init__(self, filenames):
      self._parser = ConfigParser()
      self._filenames = filenames

   def read(self):
      """Read config file"""
      try:
         self._conf = self._parser.read(self._filenames)
      except:
         exc = sys.exc_info()
         print '{}: {}'.format(exc[0].__name__, exc[1])
      if not self._conf:
         raise ValueError('No file(s) found: {}!'.format(self._filenames))

      # parse options
      self._mvas = self._parser.sections()
      for mva in self._mvas:
         options = {}
         for opt in self._parser.options(mva):
            value = self._parser.get(mva, opt)
            if opt.find('vars') >= 0 or opt.find('spectator') >= 0:
               options[opt] = [el.strip(',') for el in value.split()]
            elif opt.find('cut') >= 0:
               options[opt] = TCut(value)
            else:
               options[opt] = value

            # property list (after cleaning, no internal props)
            valid_props = [prop for prop in dict(vars(TMVAconfig))
                           if prop.find('_') != 0]
            # make TMVAconfig object
            tmva_conf = TMVAconfig(mva)
            for opt in options:
               if opt in valid_props:
                  setattr(tmva_conf, opt, options[opt])
               else:
                  print 'Unknown option `{}\' in `{}\' section, ignoring.'\
                     .format(opt, mva)
            setattr(self, mva, tmva_conf)

      # return # of MVA configs read
      return len(self._mvas)

   def write(self, filename):
      """Write config file"""
      return NotImplemented

   def append(self, filename):
      """Update config file"""
      return NotImplemented

   def mvas(self):
      """List of MVAs in config file"""
      return self._mvas

   def get_mva_config(self, mva):
      """Retrun MVA config"""
      return self.mva
