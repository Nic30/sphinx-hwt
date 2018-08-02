# sphinx-hwt

[![Travis-ci Build Status](https://travis-ci.org/Nic30/sphinx-hwt.png?branch=master)](https://travis-ci.org/Nic30/sphinx-hwt)[![PyPI version](https://badge.fury.io/py/sphinx-hwt.svg)](http://badge.fury.io/py/sphinx-hwt)[![Coverage Status](https://coveralls.io/repos/github/Nic30/sphinx-hwt/badge.svg?branch=master)](https://coveralls.io/github/Nic30/sphinx-hwt?branch=master)[![Documentation Status](https://readthedocs.org/projects/hwtlib/badge/?version=latest)](http://hwtlib.readthedocs.io/en/latest/?badge=latest)
[![Python version](https://img.shields.io/pypi/pyversions/sphinx-hwt.svg)](https://img.shields.io/pypi/pyversions/sphinx-hwt.svg)

Extension for Sphinx document generator. Add automatically generated schemes and other visual documentation of hardware.
Currently mainly for [HWT library](https://github.com/Nic30/hwt.git) (but VHDL,Verilog -> HWT is possible).


## Feature list (will add in 2018-7-xx)
* generate interactive schematic for Unit instances (= module in verilog, entity + architecutere in VHDL).
  * zoom, pan, dynamic colapsing, net-select, searching and filtering
  * schematic rendered by [d3-hwschematic library](https://github.com/Nic30/d3-hwschematic)
  * Unit instances to graph conversion by [hwtGraph library](https://github.com/Nic30/hwtGraph)
* signal waves by [d3-wave library](https://github.com/Nic30/d3-wave)
