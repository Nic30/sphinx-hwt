#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.command.sdist import sdist as _sdist
from os import path
import os
from os.path import dirname, abspath
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from shutil import copyfile
from shutil import rmtree
from subprocess import check_call
import sys

from setuptools import find_packages, setup, Command


TOP_DIR = dirname(abspath(__file__))

JS_FILES = [
    "node_modules/d3/dist/d3.js",
    "node_modules/d3-hwschematic/dist/d3-hwschematic.js",
    "node_modules/d3-hwschematic/src/elk/elk-worker.js"]


def npm_installation_check():
    try:
        check_call(["npm", "--version"])
    except Exception:
        return False
    return True


def run_npm_install():
    my_env = os.environ.copy()
    # PYTHONPATH has to be removed because webworker-threads (d3-hwschematic -> elk -> )
    # has install time dependency on python2 and PYTHONPATH 
    # overrideds python2 import paths
    if "PYTHONPATH" in my_env:
        del my_env["PYTHONPATH"]
    origCwd = os.getcwd()
    try:
        print("installing npm packages in ", TOP_DIR)
        os.chdir(TOP_DIR)
        check_call(["npm", "install"], env=my_env)
    finally:
        os.chdir(origCwd)


# from setuptools.command.install import install
def read(filename):
    with open(filename) as fp:
        return fp.read().strip()


class bdist_egg(_bdist_egg):

    def run(self):
        self.run_command('build_npm')
        _bdist_egg.run(self)


class sdist_with_npm(_sdist):

    def run(self):
        self.run_command('build_npm')
        _sdist.run(self)


class build_npm(Command):
    description = 'build javascript and CSS from NPM packages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        has_npm = npm_installation_check()
        if has_npm:
            run_npm_install()
        else:
            print("Warning: npm not installed using prebuilded js files!",
                  file=sys.stderr)
        """
        Download npm packages required by package.json and extract required
        files from them
        """
        for js in JS_FILES:
            downloaded_js_name = os.path.join(TOP_DIR, js)
            installed_js_name = os.path.join(TOP_DIR, "sphinx_hwt", "html", js)
            if has_npm:
                assert os.path.exists(downloaded_js_name), downloaded_js_name
                os.makedirs(os.path.dirname(installed_js_name), exist_ok=True)
                copyfile(downloaded_js_name, installed_js_name)
                print("copy generated from NPM packages", installed_js_name)
            else:
                if os.path.exists(installed_js_name):
                    print("using prebuilded", installed_js_name)
                else:
                    raise Exception("Can not find npm,"
                                    " which is required for the installation "
                                    "and this is pacpage has not js prebuilded")


class build(_build):
    sub_commands = [('build_npm', None)] + _build.sub_commands


class clean(_clean):

    def run(self):
        root = dirname(__file__)
        for d in ["node_modules", "sphinx_hwt/html/node_modules",
                  "sphinx_hwt.egg-info", "dist", "build"]:
            rmtree(path.join(root, d), ignore_errors=True)

        _clean.run(self)


setup(
    name='sphinx-hwt',
    version='1.6',
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
        'hwtGraph>=0.7',  # converts HWT Units to schematics
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        'Environment :: Plugins',
        'Framework :: Sphinx :: Extension',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    cmdclass={
        'build': build,  # clean generated files
        'bdist_egg': bdist_egg,
        'build_npm': build_npm,  # generate js files from npm packages
        'sdist': sdist_with_npm,
        'clean': clean,
    },
    package_data={
        'sphinx_hwt': ['*.html', '*.css', "*.js"]
    },
    include_package_data=True,
    zip_safe=False,
)
