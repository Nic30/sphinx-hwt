#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test


class HwtComponents_directive_TC(unittest.TestCase):

    def test_components_2lvl(self):
        run_test("test_components_2lvl")


if __name__ == "__main__":
    unittest.main()
