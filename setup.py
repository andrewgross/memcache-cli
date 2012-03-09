# #!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <andrew.w.gross@gmail.com> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet
# some day, and you think this stuff is worth it, you can buy me a
# beer in return Poul-Henning Kamp
# ----------------------------------------------------------------------------

import os
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('memcachecli'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

setup(name='memcache-cli',
    version='0.1.0',
    description='memcache command line interface',
    author=u'Andrew Gross',
    author_email='andrew.w.gross@gmail.com',
    url='http://github.com/andrewgross/memcache-cli',
    packages=['memcachecli'],
    install_requires=[
        "python-memcached",
    ],
    entry_points={
        'console_scripts': ['memcache-cli = memcachecli.main:main'],
    },

)
