import unittest

__author__ = 'sheepy'


def load_tests_from_class(clazz):
    """ Loading all tests by class name and returning the tests found by this """
    return [test for test in unittest.TestLoader().loadTestsFromTestCase(clazz)]

def handle_single_run(test_to_call, suites):
    clazz, method = test_to_call.split(".")
    filtered = [[e for e in suite if clazz in str(e) and method in str(e)] for suite in suites]
    filtered = [e for e in filtered if len(e) > 0]

    if len(filtered) == 0:
        print "[Error] No Test Cases found for {}".format(test_to_call)
    elif len(filtered) == 1:
        suite_with_test = filtered[0]
        if len(suite_with_test) == 1:
            # Just run it
            test = suite_with_test[0]
            unittest.TextTestRunner(verbosity=2).run(test)
        else:
            print "[Error] Same test case found in the same suite o.O?!"
    else:
        print "[Error] Same test case found in multiple suites!"