#!/usr/bin/env python3
'''Setup script for lima (Lightweight Marshalling of Python 3 Objects).'''

import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# require Python 3.3 or newer
assert sys.version_info >= (3, 3), 'Python 3.3 oder newer required.'


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = []

    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def find_version(path):
    '''Search version identifier in source file and return it.'''
    with open(path, encoding='utf-8') as f:
        contents = f.read()
    match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                      contents, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Can't find version identifier.")


def read(path):
    '''Return contents of utf-8 encoded text file'''
    with open(path, encoding='utf-8') as f:
        return f.read()


setup(
    name='lima',
    version=find_version(os.path.join('lima', '__init__.py')),
    description='Lightweight Marshalling of Python 3 Objects.',
    long_description=read('README.rst'),
    keywords='marshal marshalling serialization api json rest',
    url='https://lima.readthedocs.org',
    author='Bernhard Weitzhofer',
    author_email='bernhard@weitzhofer.org',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
