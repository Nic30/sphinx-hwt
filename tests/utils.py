from io import StringIO
from os import path
import os
from shutil import rmtree
from sphinx.cmd.build import main as sphinx_main
from sphinx.ext.apidoc import main as apidoc_main
import sys
from types import ModuleType
from unittest.mock import patch

cwd = os.path.dirname(path.realpath(__file__))

# allow to use this extension
sys.path.append(path.join(cwd, ".."))


def _run_test():
    rmtree("doc/", ignore_errors=True)
    rmtree("doc_build/", ignore_errors=True)

    # [OPTIONS] -o <OUTPUT_PATH> <MODULE_PATH> [EXCLUDE_PATTERN, ...]
    # apidoc_main(["-h"])
    ret = apidoc_main(["--module-first", "--force", "--full",
                       "--output-dir", "doc/", "."])

    if ret != 0:
        raise AssertionError("apidoc_main failed with err %d" % ret)

    # -b buildername
    # -a If given, always write all output files. The default is to only write output files for new and changed source files. (This may not apply to all builders.)
    # -E Don’t use a saved environment (the structure caching all cross-references), but rebuild it completely. The default is to only read and parse source files that are new or have changed since the last run.
    # -C Don’t look for a configuration file; only take options via the -D option.
    # [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]

    # sphinx_main(["-h"])
    ret = sphinx_main(["-b", "html", "-E",
                       "-c", cwd,
                       "doc/",
                       "doc_build/",
                       ])
    if ret != 0:
        raise AssertionError("sphinx_main failed with err %d" % ret)


def run_test(test_name, mock_stdout=False, mock_stderr=False):
    """
    Build documentation in specified test folder
    """
    test_path = path.join(cwd, test_name)
    try:
        sys.path.append(path.abspath(test_path))
        os.chdir(test_path)
        # allow test modules import

        stderr = sys.stderr
        if mock_stderr:
            stderr = StringIO()

        stdout = sys.stdout
        if mock_stdout:
            stdout = StringIO()

        @patch("sys.stdout", new=stdout)
        @patch("sys.stderr", new=stderr)
        def mocked_run_test():
            return _run_test()

        return mocked_run_test()
    finally:
        if not mock_stdout:
            sys.stdout.flush()
        if not mock_stderr:
            sys.stderr.flush()

        os.chdir(cwd)
        sys.path.pop()
        for name, m in list(sys.modules.items()):
            if isinstance(m, ModuleType) \
                    and hasattr(m, "__file__") \
                    and m.__file__ is not None \
                    and m.__file__.startswith("./"):
                del sys.modules[name]
