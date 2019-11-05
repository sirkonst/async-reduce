#!/usr/bin/env python

import os
from setuptools import setup
from versioning import version


localversion = os.environ.get('LOCALVERSION', 'auto') or None

setup(
    setup_requires=[
        'setuptools >= 30.4'
    ],
    version=version(0, 3, localversion=localversion),
)
