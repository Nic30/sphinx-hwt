#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    license='BSD',
    keywords='sphinx documentation HWT FPGA hardware VHDL System Verilog schematic wave',
    url='https://github.com/Nic30/sphinx-hwt',
    packages=find_packages(exclude=['tests*']),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[
        'Sphinx>=1.7.6',
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
    include_package_data=True,
)