#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test


class HwtBuildReport_directive_TC(unittest.TestCase):

    def test_buildReport_simple(self):
        run_test("test_buildReport_simple")

if __name__ == "__main__":
    unittest.main()
