#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: borja@libcrack.so
# Date: Wed Jan 28 16:35:57 CET 2015

import re
import os

from setuptools import find_packages, setup


def read(relpath):
    '''
    Return string containing the contents of the file at *relpath* relative to
    this file.
    '''
    cwd = os.path.dirname(__file__)
    abspath = os.path.join(cwd,
            os.path.normpath(relpath))
    with open(abspath) as f:
        return f.read()

NAME = 'dswx-docx'
VERSION = re.search("__version__ = '([^']+)'",
        read('telegram/__init__.py')).group(1)
#VERSION = read('VERSION').strip()
DESCRIPTION = 'Telegram Bot module.'
KEYWORDS = 'telegram bot'
AUTHOR = 'Borja Ruiz'
AUTHOR_EMAIL = 'borja@libcrack.so'
URL = 'http://www.libcrack.so'
LICENSE = read('LICENSE')
PACKAGES = find_packages(exclude=['tests', 'tests.*'])
PACKAGE_DATA = {'telegrambot': ['data/*']}
PACKAGE_DIR = {'telegrambot': ['telegrambot']}
INSTALL_REQUIRES = [
    'python-daemon',
    'requests',
    'twisted',
    ]
#TEST_SUITE = 'tests'
#TESTS_REQUIRE = ['behave', 'mock', 'pyparsing', 'pytest']
LONG_DESC = read('README.md') + '\n\n' + read('CHANGES')
PLATFORMS = ['Linux']
PY_MODULES = [
    'telegrambot/config',
    'telegrambot/console',
    'telegrambot/logger',
    'telegrambot/telegrambot',
    ]
PROVIDES = ['telegrambot']

CLASSIFIERS = [
    'Development Status :: 3 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: Other/Propietary License',
    'Operating System :: OS Independent',
    'Operating System :: POSIX :: Linux',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

PARAMS = {
    'platforms':        PLATFORMS,
    'name':             NAME,
    'version':          VERSION,
    'description':      DESCRIPTION,
    'keywords':         KEYWORDS,
    'long_description': LONG_DESC,
    'author':           AUTHOR,
    'author_email':     AUTHOR_EMAIL,
    'url':              URL,
    'license':          LICENSE,
    'packages':         PACKAGES,
    'package_dir':      PACKAGE_DIR,
    'package_data':     PACKAGE_DATA,
    'py_modules':       PY_MODULES,
    'provides':         PROVIDES,
    'requires':         INSTALL_REQUIRES,
    'install_requires': INSTALL_REQUIRES,
    #'tests_require':    TESTS_REQUIRE,
    #'test_suite':       TEST_SUITE,
    'classifiers':      CLASSIFIERS,
}

setup(**PARAMS)

# vim:ts=4 sts=4 tw=79 expandtab:
