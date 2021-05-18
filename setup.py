#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for vocab.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import require, VersionConflict
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)


if __name__ == "__main__":
    setup(
        name="Vocab",
        version="0.0.2",
        author="Denis Samuilik",
        author_email="denis.samuilik1990@gmail.com",
        entry_points={
            "console_scripts": [
                "vocab = vocab.__main__:main",
            ],
        },

    )
