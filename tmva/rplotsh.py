#!/usr/bin/env python
# coding=utf-8

# argument parsing
from argparse import ArgumentParser
from utils import (_import_args)

optparser = ArgumentParser(description=__doc__)
optparser.add_argument('filenames', nargs='+', help='ROOT files')
options = optparser.parse_args()

# ROOT
from fixes import ROOT
from ROOT import gDirectory, gROOT
rootdir = gDirectory.GetDirectory('')


import cmd
class empty(cmd.Cmd):
    def emptyline(self):
        pass

class rshell(cmd.Cmd):
    """Shell-like navigation commands for ROOT files"""

    ls_parser = ArgumentParser()
    ls_parser.add_argument('-l', action='store_true', dest='showtype', default=False)
    ls_parser.add_argument('objs', nargs='*')

    pwd = gDirectory.GetDirectory('')
    prompt = '{}> '.format(pwd.GetName())

    @classmethod
    def _bytes2kb(cls, Bytes):
        unit = 1
        while Bytes >= 1024:
            Bytes /= 1024.0
            unit += 1
        if unit == 1: return Bytes
        elif unit == 2: unit = 'KB'
        elif unit == 3: unit = 'MB'
        elif unit == 4: unit = 'GB'
        return '{:.1f}{}'.format(Bytes, unit)

    def completion_helper(self, text, line, begidx, endidx, comp_type):
        self.comp_f = map(lambda i: i + ':', filenames) # TFiles
        if self.pwd == rootdir:
            completions = self.comp_f
        else:
            path = os.path.split(text)
            if path[0]: thisdir = self.pwd.GetDirectory(path[0])
            else: thisdir = self.pwd
            if comp_type == 'dir':
                completions = self._get_paths(thisdir, dirs = True)
            if comp_type == 'path':
                completions = self._get_paths(thisdir, dirs = False)
            if path[0]:
                completions = ['/'.join((path[0],i)) for i in completions]
            completions += self.comp_f
        if not text:
            return completions
        else:
            return filter(lambda i : str.startswith(i, text), completions)

    def _get_paths(self, thisdir, dirs = False):
        keys = thisdir.GetListOfKeys()
        if dirs:
            _is_dir = lambda key: ROOT.TClass.GetClass(key.GetClassName())\
                                             .InheritsFrom(ROOT.TDirectoryFile.Class())
            keys = filter(_is_dir, thisdir.GetListOfKeys())
        return [k.GetName() for k in keys]

    def precmd(self, line):
        self.oldpwd = self.pwd
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        self.pwd = gDirectory.GetDirectory('')
        dirn = self.pwd.GetName()
        if len(dirn) > 20:
            dirn = '{}..{}'.format(dirn[0:9], dirn[-9:])
        self.prompt = '{}> '.format(dirn)
        return cmd.Cmd.postcmd(self, stop, line)

    def _list_objs(self, objs, showtype=False, depth=0, indent=''):
        for obj in objs:
            objn = obj                 # for error msg
            if isinstance(obj, str): # when invoked w/ args
                if obj.find(':') < 0: # not a file path: file:/path
                    obj = self.pwd.GetKey(obj)
                else:
                    tokens = obj.split(':', 1)
                    obj = gROOT.GetListOfFiles().FindObject(tokens[0])
                    if len(tokens[1]) > 0:
                        obj = obj.GetKey(tokens[1])
            if obj:             # NB: obj is TFile or TKey
                name = obj.GetName()
                if isinstance(obj, ROOT.TKey):
                    cname = obj.GetClassName()
                else:
                    cname = obj.ClassName()
                ocls = ROOT.TClass.GetClass(cname)
                if isinstance(obj, ROOT.TKey):
                    fsize = self._bytes2kb(obj.GetNbytes())
                    usize = self._bytes2kb(obj.GetObjlen())
                if showtype:
                    fmt = indent + '{cls:<20}{fs:>8}({us:>8}) {nm}{m}'
                else:
                    fmt = indent + '{nm}{m}'
                if ocls.InheritsFrom(ROOT.TFile.Class()):
                    print(fmt.format(cls = cname, nm = name, m = ':',
                                     fs = '-', us = '-'))
                elif ocls.InheritsFrom(ROOT.TDirectoryFile.Class()):
                    print(fmt.format(cls = cname, nm = name, m = '/',
                                     fs = fsize, us = usize))
                else:
                    print(fmt.format(cls = cname, nm = name, m = '',
                                     fs = fsize, us = usize))
                if depth and ocls.InheritsFrom(ROOT.TDirectoryFile.Class()):
                    if depth > 0: tmp = depth -1
                    else: tmp = depth
                    self._list_objs(obj.ReadObj().GetListOfKeys(), showtype, tmp, indent+' ')
            else:
                print('ls: cannot access `{}\': No such object'.format(objn))

    def do_ls(self, args=''):
        """List contents of a directory/file. (see `pathspec')"""
        opts = self.ls_parser.parse_args(args.split())
        if opts.objs:           # w/ args
            self._list_objs(opts.objs, opts.showtype, 1)
        else:                   # no args
            # can't access files trivially when in rootdir
            if self.pwd == rootdir: # PyROOT
                for f in rootdir.GetListOfFiles():
                    print('{}:'.format(f.GetName()))
            else:                   # in a root file
                self._list_objs(self.pwd.GetListOfKeys(), opts.showtype)

    def complete_ls(self, text, line, begidx, endidx):
        return self.completion_helper(text, line, begidx, endidx, 'path')

    def do_cd(self, args=''):
        """Change directory to specified directory. (see `pathspec')"""
        self.pwd.cd(args)

    def complete_cd(self, text, line, begidx, endidx):
        return self.completion_helper(text, line, begidx, endidx, 'dir')

    def help_pathspec(self):
        msg  = "Paths inside the current file can be specified in the usual way:\n"
        msg += "- full path: /dir1/dir2\n"
        msg += "- relative path: ../dir1\n\n"

        msg += "Paths in other root files have to be preceded by the file name\n"
        msg += "and a colon:\n"
        msg += "- file path: myfile.root:/dir1/dir2\n\n"

        msg += "See: TDirectoryFile::cd(..) in ROOT docs"
        print(msg)

class rplotsh(rshell,empty):
    """Interactive plotting interface for ROOT files"""

    def do_EOF(self, line):
        return True

    def postloop(self):
        print


if __name__ == '__main__':
    # history file for interactive use
    import atexit, readline, os, sys
    history_path = '.rplotsh'
    def save_history(history_path=history_path):
        import readline
        readline.write_history_file(history_path)

    if os.path.exists(history_path):
        readline.read_history_file(history_path)

    atexit.register(save_history)
    del atexit, readline, save_history, history_path

    locals().update(_import_args(options))
    rfiles = [ROOT.TFile.Open(f, 'read') for f in filenames]
    rootdir.cd()

    # command loop
    try:
        rplotsh_inst = rplotsh()
        rplotsh_inst.cmdloop()
    except KeyboardInterrupt:
        rplotsh_inst.postloop()
        sys.exit(1)
