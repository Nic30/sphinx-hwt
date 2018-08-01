#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from os import path
from os.path import dirname
from setuptools import find_packages, setup, Command
from shutil import rmtree
import sys

from setuptools.command.bdist_egg import bdist_egg as _bdist_egg

try:
    from _js_install import find_extra_js_files_in_npm
except ImportError:
    sys.path.append(dirname(__file__))
    from _js_install import find_extra_js_files_in_npm
    sys.path.pop()


# from setuptools.command.install import install
def read(filename):
    with open(filename) as fp:
        return fp.read().strip()


class bdist_egg(_bdist_egg):

    def run(self):
        self.run_command('build_npm')
        _bdist_egg.run(self)


class build_npm(Command):
    description = 'build javascript and CSS from NPM packages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for f in find_extra_js_files_in_npm():
            print("copy generated from NPM packages", f)


class build(_build):
    sub_commands = _build.sub_commands + [('build_npm', None)]


class clean(_clean):

    def run(self):
        root = dirname(__file__)
        for d in ["node_modules", "sphinx_hwt/html/node_modules"]:
            rmtree(path.join(root, d), ignore_errors=True)

        _clean.run(self)

        
setup(
    name='sphinx-hwt',
    version='0.2',
    author="Michal Orsak",
    author_email="michal.o.socials@gmail.com",
    description="Sphinx extension to produce interactive schematic for hardware writen in HWT",
    license='BSD-3-Clause',
    keywords='sphinx documentation HWT FPGA hardware VHDL System Verilog schematic wave',
    url='https://github.com/Nic30/sphinx-hwt',
    packages=find_packages(exclude=['tests*']),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[
        'sphinx>=1.7.6',  # base sphinx doc generator
        'hwtGraph>=0.4',  # converts HWT Units to schematics
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    cmdclass={
        'build': build,
        'bdist_egg': bdist_egg,
        'build_npm': build_npm,
        'clean': clean,
    },
    package_data={
        'sphinx_hwt': ['*.html', '*.css', "*.js"]
    },
    include_package_data=True,
    zip_safe=False,
)
