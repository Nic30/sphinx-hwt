#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test


class HwtAutodoc_directive_TC(unittest.TestCase):

    def test_autodoc_HwIO(self):
        run_test("test_autodoc_HwIO")

    def test_autodoc_HwModule(self):
        run_test("test_autodoc_HwModule")


if __name__ == "__main__":
    unittest.main()
