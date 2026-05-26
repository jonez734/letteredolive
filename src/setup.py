#!/usr/bin/env python3

import os
import time
from setuptools import setup

r = 1
v = os.environ.get("VERSION")
if v is None:
    v = time.strftime("%Y%m%d%H%M")

projectname = "letteredolive"
packagename = "shell"

setup(
    name=projectname,
    version=v,
    author="zoidtechnologies.com",
    author_email=f"{projectname}@projects.zoidtechnologies.com",
    license="GPLv2",
    scripts=["bin/bbs", "bin/shell"],
    requires=["bbsengine6"],
    packages=[packagename],
    provides=[projectname],
    url=f"https://projects.zoidtechnologies.com/{projectname}/",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users",
        "Operating System :: POSIX",
        "Topic :: Terminals",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
)
