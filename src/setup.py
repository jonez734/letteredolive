#!/usr/bin/env python3

#from distutils.core import setup
from setuptools import setup

import time

v = time.strftime("%Y%m%d%H%M")
projectname = "letteredolive"

setup(
  name=projectname,
  version=v,
  author="zoidtechnologies.com",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  license="GPLv2",
  scripts=["../bin/bbs", "../bin/letteredolive"],
  requires=["ttyio5", "bbsengine5"],
  packages=["letteredolive"],
  url="https://projects.zoidtechnologies.com/%s/" % (projectname),
  classifiers=[
    "Programming Language :: Python :: 3.11",
    "Environment :: Console",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: End Users",
    "Operating System :: POSIX",
    "Topic :: Terminals",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",

  ],
)
