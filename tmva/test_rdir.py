#!/usr/bin/env python

import unittest

from rdir import pathspec
class test_pathspec(unittest.TestCase):
    def setUp(self):
        self.full_path = pathspec('foo.root:/bar/baz')
        self.only_rfile1 = pathspec('foo.root')
        self.only_rfile2 = pathspec('foo.root:')
        self.abs_rpath = pathspec('/foo/bar/baz')
        self.rel_rpath1 = pathspec('foo/bar/baz')
        self.rel_rpath2 = pathspec('../../foo/bar/baz')
        self.rpath_no_slash = pathspec('foo/bar/baz/')

    def test_full_path(self):
        self.assertTrue(self.full_path.rfile)
        self.assertTrue(self.full_path.rpath)
        self.assertFalse(self.full_path.relative)

    def test_rfile(self):
        self.assertTrue(self.only_rfile1.norpath)
        self.assertTrue(self.only_rfile2.norpath)
        self.assertTrue(self.abs_rpath.norfile)
        self.assertTrue(self.rel_rpath1.norfile)
        self.assertTrue(self.rel_rpath2.norfile)

    def test_rpath(self):
        self.assertFalse(self.abs_rpath.relative)
        self.assertTrue(self.rel_rpath1.relative)
        self.assertTrue(self.rel_rpath2.relative)
        self.assertLess(self.rpath_no_slash.rpath.find('/', -1), 0)
        self.assertRaises(ValueError, pathspec, 'foo.root:../bar/baz')


import os
from fixes import ROOT
from ROOT import gDirectory, TFile

from rdir import savepwd
class test_savepwd(unittest.TestCase):
    def setUp(self):
        self.rfile = TFile.Open('/tmp/test_savepwd.root', 'recreate')
        self.dir1 = self.rfile.mkdir('dir1')
        self.dir2 = self.rfile.mkdir('dir2')

    def tearDown(self):
        os.remove('/tmp/test_savepwd.root')

    def test_restore_pass(self):
        self.dir1.cd()
        oldpwd = gDirectory.GetName()
        with savepwd():
            self.dir2.cd()
        self.assertEqual(oldpwd, gDirectory.GetName())

    def test_restore_fail(self):
        self.dir1.cd()
        oldpwd = gDirectory.GetName()
        try:
            with savepwd():
                self.dir2.cd()
                raise KeyboardInterrupt('Testing')
        except:
            pass
        self.assertEqual(oldpwd, gDirectory.GetName())


from rdir import Rdir
class test_Rdir(unittest.TestCase):
    def setUp(self):
        """Make ROOT files with some contents.

        Structure:

          /tmp/test_Rdir[0,1].root:/dira/hista
          /tmp/test_Rdir[0,1].root:/dirb/histb
          /tmp/test_Rdir[0,1].root:/hist[0,1]

        """
        self.fnames, self.rfiles = [], []
        for i in xrange(2):
            self.fnames.append('/tmp/test_Rdir{}.root'.format(i))
            self.rfiles.append(TFile.Open(self.fnames[-1], 'recreate'))

        for i, f in enumerate(self.rfiles):
            rdir = f.mkdir('dira')
            rdir.WriteTObject(ROOT.TH1C('hista', '', 10, 0, 10))

            rdir = f.mkdir('dirb')
            rdir.WriteTObject(ROOT.TH1C('histb', '', 10, 0, 10))

            f.WriteTObject(ROOT.TH1C('hist{}'.format(i), '', 10, 0, 10))

        for f in self.rfiles:
            f.Write()
            f.Close()

    def tearDown(self):
        for fname in self.fnames:
            os.remove(fname)

    def test_init(self):
        self.assertTrue(Rdir(self.fnames))
        self.assertRaises(TypeError, Rdir, self.rfiles)

    def test_get_dir(self):
        rdir_helper = Rdir(self.fnames)
        self.assertTrue(rdir_helper.get_dir('/tmp/test_Rdir1.root:/dira'))
        self.assertTrue(rdir_helper.get_dir('/tmp/test_Rdir1.root:'))
        self.assertTrue(rdir_helper.get_dir('/tmp/test_Rdir1.root'))
        # not a directory
        self.assertFalse(rdir_helper.get_dir('/tmp/test_Rdir1.root:/dira/hista'))
        # non-existent
        self.assertFalse(rdir_helper.get_dir('/tmp/test_Rdir1.root:/boohoo'))

    def test_ls(self):
        rdir_helper = Rdir(self.fnames)

        keys_t = rdir_helper.ls('/tmp/test_Rdir0.root:/dirb')
        keys_r = rdir_helper.files[0].GetDirectory('/dirb').GetListOfKeys()
        res = map(lambda i, j: i.GetName() == j.GetName(), keys_t, keys_r)
        self.assertTrue(reduce(lambda i, j: i and j, res), msg='Keys do not match')

        # FIXME: change files to see if any effects show up, need better test
        keys_t = rdir_helper.ls('/tmp/test_Rdir1.root')
        keys_r = rdir_helper.files[1].GetListOfKeys()
        res = map(lambda i, j: i.GetName() == j.GetName(), keys_t, keys_r)
        self.assertTrue(reduce(lambda i, j: i and j, res), msg='Keys do not match')

    def test_ls_names(self):
        rdir_helper = Rdir(self.fnames)
        # FIXME: Is using assertItemsEqual(..) correct?  Does it
        # compare elements, or just count?
        keys_t = rdir_helper.ls_names('/tmp/test_Rdir0.root:/hist0')
        keys_r = [rdir_helper.files[0].GetKey('hist0').GetName()]
        self.assertItemsEqual(keys_r, keys_t)

        keys_t = rdir_helper.ls_names('/tmp/test_Rdir1.root')
        keys_r = [k.GetName() for k in rdir_helper.files[1].GetListOfKeys()]
        self.assertItemsEqual(keys_r, keys_t)

    def test_read(self):
        rdir_helper = Rdir(self.fnames)
        objs_t = rdir_helper.read('/tmp/test_Rdir1.root')
        objs_r = [k.ReadObj() for k in rdir_helper.files[1].GetListOfKeys()]
        res = map(lambda i, j: i.GetName() == j.GetName(), objs_t, objs_r)
        self.assertTrue(reduce(lambda i, j: i and j, res), msg='Keys do not match')

    def test_filter(self):
        rdir_helper = Rdir(self.fnames)
        keys_t = rdir_helper.ls('/tmp/test_Rdir0.root:',
                                robj_t = ROOT.TDirectoryFile)
        keys_r = [k for k in rdir_helper.files[0].GetListOfKeys()
                  if ROOT.TClass.GetClass(k.GetClassName()) \
                  .InheritsFrom(ROOT.TDirectoryFile.Class())]
        res = map(lambda i, j: i.GetName() == j.GetName(), keys_t, keys_r)
        self.assertTrue(reduce(lambda i, j: i and j, res), msg='Keys do not match')
