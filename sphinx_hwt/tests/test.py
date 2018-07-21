from io import StringIO
from os import path
import os
from shutil import rmtree
from sphinx.cmdline import main as sphinx_main
from sphinx.ext.apidoc import main as apidoc_main
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


pwd = os.path.dirname(path.realpath(__file__))

# allow to use this extension
sys.path.append(path.join(pwd, ".."))


def assert_err_on_exit(err):
    if err != 0:
        raise AssertionError("Test exit with %d" % err)


# @patch('sys.exit', new=assert_err_on_exit)
# @patch('sys.stdout', new_callable=StringIO)
def _run_test(mock_stdout):
    rmtree("doc/", ignore_errors=True)
    rmtree("doc_buld/", ignore_errors=True)

    # [OPTIONS] -o <OUTPUT_PATH> <MODULE_PATH> [EXCLUDE_PATTERN, ...]
    # apidoc_main(["-h"])
    ret = apidoc_main(["--module-first", "--force", "--full",
                       "--output-dir", "doc/", "."])

    if ret != 0:
        sys.stderr.flush()
        if mock_stdout is not None:
            sys.stdout.flush()

        raise AssertionError("apidoc_main failed with err %d" % ret)

    # -b buildername
    # -a If given, always write all output files. The default is to only write output files for new and changed source files. (This may not apply to all builders.)
    # -E Don’t use a saved environment (the structure caching all cross-references), but rebuild it completely. The default is to only read and parse source files that are new or have changed since the last run.
    # -C Don’t look for a configuration file; only take options via the -D option.
    # [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]

    # sphinx_main(["-h"])
    ret = sphinx_main(["-b", "html", "-E",
                       "-c", pwd,
                       "doc/",
                       "doc_build/",
                       ])
    if ret != 0:
        sys.stderr.flush()
        if mock_stdout is not None:
            sys.stdout.flush()
        raise AssertionError("sphinx_main failed with err %d" % ret)

    return mock_stdout


def run_test(name):
    """
    Build documentation in specified test folder
    """
    try:
        os.chdir(name)
        # allow test modules import
        sys.path.append(".")

        return _run_test(None)
    finally:
        os.chdir(pwd)
        sys.path.pop()
        for name, m in list(sys.modules.items()):
            if isinstance(m, ModuleType) \
                    and hasattr(m, "__file__") \
                    and m.__file__.startswith("./"):
                del sys.modules[name]


class HwtSchematic_directive_TC(unittest.TestCase):

    def test_another_text(self):
        run_test("test_another_text")

    def test_module(self):
        run_test("test_module")

    def test_package(self):
        run_test("test_package")

    def test_not_a_Unit(self):
        with self.assertRaises(AssertionError):
            run_test("test_not_a_Unit")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(HwtSchematic_directive_TC('test_not_a_Unit'))
    suite.addTest(unittest.makeSuite(HwtSchematic_directive_TC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
