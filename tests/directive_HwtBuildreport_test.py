#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test

# copy database
# check if in folder _build

class HwtBuildReport_directive_TC(unittest.TestCase):

    def test_buildreport_simple(self):
        run_test("test_buildreport_simple")

if __name__ == "__main__":
    unittest.main()
