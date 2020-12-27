#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.utils import run_test


class HwtInterfaces_directive_TC(unittest.TestCase):

    def test_interfaces_Unit_intf(self):
        run_test("test_interfaces_Unit_intf")

    def test_interfaces_Unit_intf_reference(self):
        run_test("test_interfaces_Unit_intf_reference")

    def test_interfaces_Unit_intf_with_ivar(self):
        run_test("test_interfaces_Unit_intf_with_ivar")

    def test_interfaces_Interface_intf(self):
        run_test("test_interfaces_Interface_intf")

    def test_interfaces_Interface_intf_reference(self):
        run_test("test_interfaces_Interface_intf_reference")

    def test_interfaces_Interface_intf_with_ivar(self):
        run_test("test_interfaces_Interface_intf_with_ivar")


if __name__ == "__main__":
    unittest.main()
