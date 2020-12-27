from docutils.nodes import GenericNodeVisitor
from os import listdir
import os
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
        sch_dir = os.path.join(cwd, test_name, "doc_build/_static/hwt_schematics/")
        sch_files = [f for f in listdir(sch_dir)
                     if isfile(join(sch_dir, f))]
        self.assertEqual(len(sch_files), 3)

    def test_not_a_Unit(self):
        with self.assertRaises(AssertionError):
            run_test("test_not_a_Unit", mock_stderr=True)


class HwtParams_directive_TC(unittest.TestCase):

    def test_params_none(self):
        run_test("test_params_none")

    def test_params_2(self):
        run_test("test_params_2")

    def test_params_with_ivar(self):
        run_test("test_params_with_ivar")

    def test_params_of_unpicklable_type(self):
        run_test('test_params_of_unpicklable_type')


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


class HwtAutodoc_directive_TC(unittest.TestCase):

    def test_autodoc_Interface(self):
        run_test("test_autodoc_Interface")

    def test_autodoc_Unit(self):
        run_test("test_autodoc_Unit")


TCs = [
    HwtSchematic_directive_TC,
    HwtParams_directive_TC,
    HwtInterfaces_directive_TC,
    HwtAutodoc_directive_TC,
]

if __name__ == "__main__":
    import sys
    suite = unittest.TestSuite()
    # suite.addTest(HwtSchematic_directive_TC('test_test_speficified_constructor_nested'))
    for tc in TCs:
        suite.addTest(unittest.makeSuite(tc))
    runner = unittest.TextTestRunner(verbosity=3)
    res = runner.run(suite)
    if not res.wasSuccessful():
        sys.exit(1)

