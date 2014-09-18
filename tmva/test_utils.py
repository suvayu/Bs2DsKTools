#!/usr/bin/env python

import unittest

from fixes import ROOT
from utils import read_yaml, make_paths, path2rootdir
class test_utils(unittest.TestCase):
    def test_read_yaml(self):
        self.assertTrue(read_yaml('dsk_train_out.yaml'))

    def test_make_paths(self):
        path_dicts = make_paths(read_yaml('dsk_train_out.yaml'))
        # test 1 generic metadata field
        self.assertTrue(path_dicts[0]['title'])
        for path in path_dicts:
            self.assertTrue(path['path'])

    def test_path2rootdir(self):
        path_dicts = make_paths(read_yaml('dsk_train_out.yaml'))
        for path in path_dicts:
            rfile, rdir = path2rootdir(path['path'])
            self.assertTrue(not rfile.IsZombie())
            self.assertTrue(rdir)
