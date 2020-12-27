#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test


class HwtParams_directive_TC(unittest.TestCase):

    def test_params_none(self):
        run_test("test_params_none")

    def test_params_2(self):
        run_test("test_params_2")

    def test_params_with_ivar(self):
        run_test("test_params_with_ivar")

    def test_params_of_unpicklable_type(self):
        run_test('test_params_of_unpicklable_type')


if __name__ == "__main__":
    unittest.main()
