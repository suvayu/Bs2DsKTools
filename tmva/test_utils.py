#!/usr/bin/env python

import unittest

from fixes import ROOT
from utils import read_yaml, make_paths, path2rootdir

class test_io(unittest.TestCase):
    def setUp(self):
        self.yamlfile = 'tmva_output_description.yaml'

    def test_read_yaml(self):
        self.assertTrue(read_yaml(self.yamlfile))

    def test_make_paths(self):
        path_dicts = make_paths(read_yaml(self.yamlfile))
        # test 1 generic metadata field
        self.assertTrue(path_dicts[0]['title'])
        for path in path_dicts:
            self.assertTrue(path['path'])

    def test_path2rootdir(self):
        path_dicts = make_paths(read_yaml(self.yamlfile))
        for path in path_dicts:
            rfile, rdir = path2rootdir(path['path'])
            self.assertTrue(not rfile.IsZombie())
            self.assertTrue(rdir)

class test_hist(unittest.TestCase):
    def setUp(self):
        self.hist1 = ROOT.TH1D('hist1', '', 20, -3, 3)
        self.hist1.FillRandom('gaus', 1000)

    def test_th1integral(self):
        from utils import th1integral
        self.assertEqual(th1integral(self.hist1), 1000)
