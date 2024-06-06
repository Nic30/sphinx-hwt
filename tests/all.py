#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest

from tests.directive_HwtAutodoc_test import HwtAutodoc_directive_TC
from tests.directive_HwtComponents_test import HwtComponents_directive_TC
from tests.directive_HwtIO_test import HwtIO_directive_TC
from tests.directive_HwtParams_test import HwtParams_directive_TC
from tests.directive_HwtSchematic_test import HwtSchematic_directive_TC
from tests.directive_HwtBuildreport_test import HwtBuildReport_directive_TC

_ALL_TCs = [
    HwtSchematic_directive_TC,
    HwtParams_directive_TC,
    HwtIO_directive_TC,
    HwtAutodoc_directive_TC,
    HwtComponents_directive_TC,
    HwtBuildReport_directive_TC,
]
testLoader = unittest.TestLoader()
loadedTcs = [testLoader.loadTestsFromTestCase(tc) for tc in _ALL_TCs]
suite = unittest.TestSuite(loadedTcs)

if __name__ == "__main__":
    import sys

    runner = unittest.TextTestRunner(verbosity=2)

    try:
        from concurrencytest import ConcurrentTestSuite, fork_for_tests
        useParallelTest = True
    except ImportError:
        # concurrencytest is not installed, use regular test runner
        useParallelTest = False

    if useParallelTest:
        # Run same tests across 4 processes
        concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests())
        runner.run(concurrent_suite)
    else:
        sys.exit(not runner.run(suite).wasSuccessful())
