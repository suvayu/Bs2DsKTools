# coding=utf-8
import sys, os

# Config script for TMVA Classification and Application
# _vars entries have format varname_in_tree (float assumed)
# _combined_vars entries have format varexpression (float assumed)
# _branch_mappings is renaming the branches from the signal tree in the classification, in case the branch names don't match

from collections import Iterable


class TMVAconfig(object):
   """Config class for TMVA Classification and Application"""

   def __init__(self, name):
      self._name = name
      self._cut_sig = ''
      self._cut_bkg = ''

   def __str__(self):
      text  = 'Training session: {}\n{}\n'.format(self._name, '-'*50)
      text += 'methods:          {}\n'.format(self._methods)
      text += 'vars:             {}\n'.format(self._vars)
      text += 'combined_vars:    {}\n'.format(self._combined_vars)
      text += 'specatators:      {}\n'.format(self._spectators)
      text += 'cut_sig:          {}\n'.format(self._cut_sig)
      text += 'cut_bkg:          {}\n'.format(self._cut_bkg)
      text += 'branch_mappings:  {}\n'.format(self._branch_mappings)
      return text

   @property
   def methods(self):
      """MVA training methods"""
      return self._methods

   @methods.setter
   def methods(self, value):
      if isinstance(value, Iterable):
         self._methods = value
      else:
         self._methods = [value]

   @methods.deleter
   def methods(self):
      del self._methods

   @property
   def vars(self):
      """Normal training MVA variables"""
      return self._vars

   @vars.setter
   def vars(self, value):
      if isinstance(value, Iterable):
         self._vars = value
      else:
         self._vars = [value]

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
         self._combined_vars = [value]
   
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
         self._spectators = [value]

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
         self._branch_mappings = [value]

   @branch_mappings.deleter
   def branch_mappings(self):
      del self._branch_mappings


from ConfigParser import ConfigParser, ParsingError
from ROOT import TCut


class ConfigFile(object):
   """TMVA configuration file object, used to read/write to a file"""
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

      # parse and return number of MVA configs read successfully
      self._parse_opts()
      return len(self._sessions)

   def _parse_opts(self):
      "The config file parser"
      # parse options
      self._sessions = self._parser.sections()
      for session in self._sessions:
         options = {}
         for opt in self._parser.options(session):
            value = self._parser.get(session, opt)
            if opt.find('cut') >= 0:
               options[opt] = TCut(value)
            else:
               options[opt] = [el.strip(',') for el in value.split()]
               if opt.find('mappings') >= 0:
                  options[opt] = [m.split(':') for m in options[opt]]

            # property list (after cleaning, i.e. no internal props)
            valid_props = [prop for prop in dict(vars(TMVAconfig))
                           if prop.find('_') != 0]
            # make TMVAconfig object
            session_conf = TMVAconfig(session)
            for opt in options:
               if opt in valid_props:
                  setattr(session_conf, opt, options[opt])
               else:
                  print 'Unknown option `{}\' in `{}\' section, ignoring.'\
                     .format(opt, session)
            setattr(self, session, session_conf)

   def write(self, filename):
      """Write config file"""
      return NotImplemented

   def append(self, filename):
      """Update config file"""
      return NotImplemented

   def sessions(self):
      """List of MVAs in config file"""
      return self._sessions

   def get_session_config(self, session):
      """Retrun MVA config"""
      return getattr(self, session)
