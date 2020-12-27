#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from docutils.nodes import GenericNodeVisitor
from os import listdir
from os.path import isfile, join
import unittest

from tests.utils import cwd, run_test


class HwtSchematic_directive_TC(unittest.TestCase):

    def setUp(self):
        names_to_delete = ["visit_SchematicLink", "depart_SchematicLink"]

        for name in names_to_delete:
            if hasattr(GenericNodeVisitor, name):
                delattr(GenericNodeVisitor, name)

    def test_another_text(self):
        run_test("test_another_text")

    def test_module(self):
        run_test("test_module")

    def test_package(self):
        run_test("test_package")

    def test_package_caseSensitive(self):
        run_test("test_package_caseSensitive")

    def test_speficified_constructor(self):
        run_test("test_speficified_constructor")

    def test_speficified_constructor_nested(self):
        run_test("test_speficified_constructor_nested")

    def test_speficified_constructor_3x_nested(self):
        test_name = "test_speficified_constructor_3x_nested"
        run_test(test_name)
        sch_dir = join(cwd, test_name, "doc_build/_static/hwt_schematics/")
        sch_files = [f for f in listdir(sch_dir)
                     if isfile(join(sch_dir, f))]
        self.assertEqual(len(sch_files), 3)

    def test_not_a_Unit(self):
        with self.assertRaises(AssertionError):
            run_test("test_not_a_Unit", mock_stderr=True)


if __name__ == "__main__":
    unittest.main()
