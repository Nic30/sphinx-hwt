#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from distutils.command.install_data import install_data
from setuptools import find_packages, setup


def read(filename):
    with open(filename) as fp:
        return fp.read().strip()


setup(
    name='sphinx-hwt',
    version='0.1',
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
        'Sphinx>=1.7.6',  # base sphinx doc generator
        'hwtGraph>=0.4',  # converts HWT Units to schemes
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
    entry_points={
        "setuptools.file_finders": [
            "foobar = sphinx_hwt._js_install:find_extra_js_files_in_npm"
        ]
    },
    package_data={
        'sphinx_hwt': ['*.html', '*.css', "*.js"]
    },
    include_package_data=True,
    zip_safe=False,
)
