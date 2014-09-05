# coding=utf-8
import sys, os

# Config script for TMVA Classification and Application
# _vars entries have format varname_in_tree (float assumed)
# _combined_vars entries have format varexpression (float assumed)
# _branch_mappings is renaming the branches from the signal tree in the classification, in case the branch names don't match

from collections import Iterable


def TMVAType(name):
   """Mapping from MVA text string to TMVA.Types"""
   name = name.lower()
   if name.find('bdt') < 0:
      return TMVA.Types.kBDT
   elif name.find('llh') < 0:
      return TMVA.Types.kLikelihood
   else:
      raise ValueError('Unsupported TMVA classifier type')


class TMVAconfig(object):
   """Config class for TMVA Classification and Application"""

   def __init__(self, name):
      self._name = name
      self._cut_sig = ''
      self._cut_bkg = ''

   def __str__(self):
      text  = 'Training session : {}\n{}\n'.format(self._name, '-'*50)
      props = [prop for prop in vars(TMVAconfig) if prop.find('_') != 0]
      props += [method.lower() for method in self.methods]
      props.sort()
      for opt in props:
         text += '{0:<{width}s} : {1:<s}\n'\
            .format(opt, getattr(self, opt), width = 16)
      return text

   def _return_if(self, prop):
      if hasattr(self, prop):
         return getattr(self, prop)

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
   def sig_file(self):
      """Normal training MVA variables"""
      return self._return_if('_sig_file')

   @sig_file.setter
   def sig_file(self, value):
      if isinstance(value, Iterable):
         self._sig_file = value
      else:
         self._sig_file = [value]

   @sig_file.deleter
   def sig_file(self):
      del self._sig_file

   @property
   def bkg_file(self):
      """Normal training MVA variables"""
      return self._return_if('_bkg_file')

   @bkg_file.setter
   def bkg_file(self, value):
      if isinstance(value, Iterable):
         self._bkg_file = value
      else:
         self._bkg_file = [value]

   @bkg_file.deleter
   def bkg_file(self):
      del self._bkg_file

   @property
   def vars(self):
      """Normal training MVA variables"""
      return self._return_if('_vars')

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
      return self._return_if('_combined_vars')

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
      all_vars = []
      all_vars += self._return_if('_vars')
      all_vars += self._return_if('_combined_vars')
      return all_vars

   @property
   def spectators(self):
      """Spectator variables (not trained)"""
      return self._return_if('_spectators')

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
   def cut_both(self):
      """Common cuts on signal and background sample"""
      return TCut(self._return_if('_cut_both'))

   @cut_both.setter
   def cut_both(self, value) :
      if isinstance(value, str) or isinstance(value, TCut):
         self._cut_both = TCut(value)
      else:
         raise ValueError('Expecting a cut string or TCut')

   @cut_both.deleter
   def cut_both(self):
      del self._cut_both

   @property
   def cut_sig(self):
      """Cuts on signal sample, including common cuts (cut_both)"""
      return self.cut_both + TCut(self._return_if('_cut_sig'))

   @cut_sig.setter
   def cut_sig(self, value) :
      if isinstance(value, str) or isinstance(value, TCut):
         self._cut_sig = TCut(value)
      else:
         raise ValueError('Expecting a cut string or TCut')

   @cut_sig.deleter
   def cut_sig(self):
      del self._cut_sig

   @property
   def cut_bkg(self):
      """Cuts on background sample, including common cuts (cut_both)"""
      return self.cut_both + TCut(self._return_if('_cut_bkg'))

   @cut_bkg.setter
   def cut_bkg(self, value) :
      if isinstance(value, str) or isinstance(value, TCut):
         self._cut_bkg = TCut(value)
      else:
         raise ValueError('Expecting a cut string or TCut')

   @cut_bkg.deleter
   def cut_bkg(self):
      del self._cut_bkg

   @property
   def branch_mappings(self):
      """Input tree branch name mappings"""
      return self._return_if('_branch_mappings')

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
         if 'methods' in self._parser.options(session):
            method_opts = [el.strip(',').lower() for el in
                           self._parser.get(session, 'methods').split()]
         else:
            raise ParsingError('Mandatory field, methods, is absent.')
         for opt in self._parser.options(session):
            value = self._parser.get(session, opt)
            if opt.find('cut') >= 0:
               options[opt] = TCut(value.replace('\n','')) # remove newlines
            else:
               options[opt] = [el.strip(',') for el in value.split()]
               if opt.find('mappings') >= 0:
                  options[opt] = [m.split(':') for m in options[opt]]

         # make & set TMVAconfig object
         session_conf = TMVAconfig(session)
         map(lambda kv : setattr(session_conf, kv[0], kv[1]), options.items())
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
