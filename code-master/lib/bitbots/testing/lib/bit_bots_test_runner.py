import sys
import time
from unittest import TestResult, registerResult
from unittest.runner import _WritelnDecorator


class BitBotsTestResult(TestResult):
    """ A test result class that gatheres the results of the test runs and produces the basis
        for a pretty print result sheet.

        Used by BitBotsTestRunner
    """

    def __init__(self, stream, descriptions, verbosity):
        super(BitBotsTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

        self.test_results = {}

    def get_test_name(self, test):
        method_name, class_name = str(test).split(" ")
        class_name = class_name[1:-1]
        class_name = class_name.split(".")[-1]
        return class_name + "." + method_name

    def startTest(self, test):
        super(BitBotsTestResult, self).startTest(test)
        self.test_results[self.get_test_name(test)] = {}
        self.stream.write("[Started Test] " + self.get_test_name(test) + "\n")
        self.stream.flush()

    def addSuccess(self, test):
        super(BitBotsTestResult, self).addSuccess(test)
        self.test_results[self.get_test_name(test)] = {
            "marker": 'success'
        }

    def addError(self, test, err):
        super(BitBotsTestResult, self).addError(test, err)
        self.test_results[self.get_test_name(test)] = {
            "marker": 'error',
            "error": err[1].__repr__()
        }

    def addFailure(self, test, err):
        super(BitBotsTestResult, self).addFailure(test, err)
        self.test_results[self.get_test_name(test)] = {
            "marker": 'failure',
            "error": str(err[0]) + str(err[1])
        }

    def addSkip(self, test, reason):
        super(BitBotsTestResult, self).addSkip(test, reason)
        self.test_results[self.get_test_name(test)] = {
            "marker": 'skip',
            "error": reason
        }

    def addExpectedFailure(self, test, err):
        super(BitBotsTestResult, self).addExpectedFailure(test, err)
        self.test_results[self.get_test_name(test)] = {
            "marker": 'expected_failure',
            "error": str(err[0]) + str(err[1])
        }

    def addUnexpectedSuccess(self, test):
        super(BitBotsTestResult, self).addUnexpectedSuccess(test)
        self.test_results[self.get_test_name(test)] = {
            "marker": 'unexpected_success'
        }

    def printErrors(self):
        pass

    def printErrorList(self, flavour, errors):
        pass

    def logRunTime(self, test, run_time):
        self.stream.write("Runtime")

    def get_general_stats(self):
        success = 0
        failure = 0
        skips = 0
        for test in self.test_results:
            test_results = self.test_results[test]
            if test_results['marker'] in ["success", "expected_failure"]:
                success += 1
            elif test_results['marker'] == "skip":
                skips += 1
            else:
                failure += 1

        return success, failure, skips

class BitBotsTestRunner(object):
    """A test runner class that aggregates the results from the BitBots Tests and
       pushes it into the BitBotsTestResult for further pretty printing.
    """
    resultclass = BitBotsTestResult

    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None):
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = False
        self.buffer = buffer
        if resultclass is not None:
            self.resultclass = resultclass

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime
        #stopTestRun = getattr(result, 'logRunTime', None)
        #stopTestRun(test, timeTaken)

        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()
        return result
