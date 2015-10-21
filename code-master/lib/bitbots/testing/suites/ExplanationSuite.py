import unittest
from bitbots.testing.lib import load_tests_from_class
from bitbots.testing.lib.bitbots_test_suite import BitBotsTestSuite


class TestExplanation(unittest.TestCase):

    @unittest.skipIf(True, "This is skipping as an example.")
    def test_skip_example(self):
        pass

    @unittest.expectedFailure
    def test_expect_failure(self):
        raise ValueError()

    @unittest.expectedFailure
    def test_unexpected_success(self):
        self.assertFalse(False)

    def test_error(self):
        raise KeyError()

    def test_failure(self):
        self.assertFalse(True)

    def test_success(self):
        self.assertFalse(False)


def suite_explanation():
    suite = BitBotsTestSuite("- Explanation Suite -", "Shows how all errors are displayed.")
    suite.addTests(load_tests_from_class(TestExplanation))
    return suite
