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
@unittest.skip('Not implemented')
class test_Rdir(unittest.TestCase):
    def setUp(self):
        self.rfile1 = TFile.Open('/tmp/test_Rdir1.root', 'recreate')
        self.dir11 = self.rfile1.mkdir('dir11')
        self.dir12 = self.rfile1.mkdir('dir12')
        self.rfile2 = TFile.Open('/tmp/test_Rdir2.root', 'recreate')
        self.dir21 = self.rfile1.mkdir('dir21')
        self.dir22 = self.rfile1.mkdir('dir22')
        # FIXME: make regular objects for listing & reading

    def tearDown(self):
        os.remove('/tmp/test_Rdir1.root')
        os.remove('/tmp/test_Rdir2.root')

    def test_ls(self):
        pass

    def test_ls_names(self):
        pass

    def test_read(self):
        pass

    def test_filter(self):
        pass
