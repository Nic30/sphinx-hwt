#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test


class HwtAutodoc_directive_TC(unittest.TestCase):

    def test_autodoc_Interface(self):
        run_test("test_autodoc_Interface")

    def test_autodoc_Unit(self):
        run_test("test_autodoc_Unit")


if __name__ == "__main__":
    unittest.main()
