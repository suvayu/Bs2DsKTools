#!/usr/bin/env python
# coding=utf-8
"""
This is a setup script to use ROOT with python. It sets up the library
and include paths (equivalent to rootlogon.cc).
"""

gSystem.AddIncludePath(" -I./include")
print "Include path = %s" % gSystem.GetIncludePath()

gSystem.AddDynamicPath("./lib")
print "Dynamic path = %s" % gSystem.GetDynamicPath()
