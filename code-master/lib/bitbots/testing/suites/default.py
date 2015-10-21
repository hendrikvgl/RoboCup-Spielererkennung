from bitbots.debug.test.testComplexObjectConvertors import TestComplexObjectConverter
from bitbots.framework.tests.testFramework import TestFramework
from bitbots.locator.test.testMatcher import TestLineMatcher
from bitbots.modules.abstract.tests.testAbstractBehaviourModule import TestAbstractBehaviourodule
from bitbots.modules.abstract.tests.testAbstractInitStepActionModule import TestAbstractInitStepActionModule
from bitbots.modules.abstract.tests.testAbstractStackElement import TestAbstractStackElement
from bitbots.modules.basic.tests.ball_info_filter_module_test import TestBallInfoDataFilterModule
from bitbots.modules.basic.tests.ball_speed_module_test import TestBallSpeedModule
from bitbots.modules.basic.tests.goal_post_info_filter_module_test import TestGoalPostInfoDataFilter
from bitbots.modules.basic.tests.goalie_intersection_module_test import TestGoalieIntersectionModule
from bitbots.modules.basic.tests.local_world_model_module_test import TestLocalWorldModelModule
from bitbots.modules.basic.tests.penalizer_module_test import TestPenalizerModule
from bitbots.modules.basic.tests.vision_module_test import TestVisionModule
from bitbots.modules.behaviour.body.tests.test_body_config_accesses import TestBodyConfigAccesses
from bitbots.modules.behaviour.body.tests.test_duty_decider import TestDutyDecider
from bitbots.modules.behaviour.body.tests.test_to_to_absolute_position import TestGoToAbsolutePosition
from bitbots.modules.behaviour.head.actions.tests.testConfirm import TestConfirm
from bitbots.modules.behaviour.head.actions.tests.testHeadPanTilt import TestHeadPanTilt
from bitbots.modules.behaviour.head.tests.testHeadConfigAccesses import TestHeadConfigAccesses
from bitbots.modules.behaviour.modell.capsules.tests.test_walking_capsule import TestWalkingCapsule
from bitbots.modules.behaviour.modell.tests.test_connector import TestConnector
from bitbots.record.tests import TestCommands, TestConsole, TestAnimations
from bitbots.robot.test.test_robot import TestKinematics
from bitbots.testing.lib import load_tests_from_class
from bitbots.testing.lib.bitbots_test_suite import BitBotsTestSuite
from bitbots.util.algorithms.tests.py.testDBscan import TestDBScan
from bitbots.util.algorithms.tests.py.testKMeans import TestKMeans
from bitbots.util.test.test_kinematic_util import TestKinematicUtil
from bitbots.util.test.tests import TestMotorConnectionAnalyser
from bitbots.debug.test.testDebugFramework import TestDebugFramework


def suite_debug_framework():
    # Adding all tests to the test suite
    suite = BitBotsTestSuite("Debug Framework", "Some descriptive longer text to explain what this suite does Some descriptive longer text to explain what this suite does ")
    suite.addTests(load_tests_from_class(TestDebugFramework))
    suite.addTests(load_tests_from_class(TestComplexObjectConverter))
    return suite

def suite_abstract_elements():
    suite = BitBotsTestSuite("Abstract Elements", "All the abstract/base classes that are used in BasicModules and in the StackMachine")
    suite.addTests(load_tests_from_class(TestAbstractBehaviourodule))
    suite.addTests(load_tests_from_class(TestAbstractInitStepActionModule))
    suite.addTests(load_tests_from_class(TestAbstractStackElement))
    suite.addTests(load_tests_from_class(TestFramework))
    return suite

def suite_record_script():
    suite = BitBotsTestSuite("Record Script", "Unittests regarding the record script.")
    suite.addTests(load_tests_from_class(TestCommands))
    suite.addTests(load_tests_from_class(TestAnimations))
    suite.addTests(load_tests_from_class(TestConsole))
    return suite

def suite_basic_module_tests():
    suite = BitBotsTestSuite("Basic Modules", "All tests related to basic modules.")
    suite.addTests(load_tests_from_class(TestBallInfoDataFilterModule))
    suite.addTests(load_tests_from_class(TestBallSpeedModule))
    suite.addTests(load_tests_from_class(TestGoalPostInfoDataFilter))
    suite.addTests(load_tests_from_class(TestGoalieIntersectionModule))
    suite.addTests(load_tests_from_class(TestLocalWorldModelModule))
    suite.addTests(load_tests_from_class(TestPenalizerModule))
    suite.addTests(load_tests_from_class(TestVisionModule))
    return suite


def suite_body_behaviour_tests():
    suite = BitBotsTestSuite("Behaviour Tests (Body)", "All tests related to body behaviour.")
    suite.addTests(load_tests_from_class(TestConnector))
    suite.addTests(load_tests_from_class(TestWalkingCapsule))
    suite.addTests(load_tests_from_class(TestGoToAbsolutePosition))
    suite.addTests(load_tests_from_class(TestDutyDecider))
    suite.addTests(load_tests_from_class(TestBodyConfigAccesses))
    return suite


def suite_head_behaviour_tests():
    suite = BitBotsTestSuite("Behaviour Tests (Head)", "All tests related to head behaviour.")
    suite.addTests(load_tests_from_class(TestHeadConfigAccesses))
    suite.addTests(load_tests_from_class(TestConfirm))
    suite.addTests(load_tests_from_class(TestHeadPanTilt))
    return suite


def suite_kinematics():
    suite = BitBotsTestSuite("Kinematics", "Test cases that focus on kinematics and tools around this.")
    suite.addTests(load_tests_from_class(TestKinematics))
    suite.addTests(load_tests_from_class(TestKinematicUtil))
    return suite


def suite_algorithms():
    suite = BitBotsTestSuite("Algorithms Tests", "Test Cases that focus on capsuled algorithms that are used in the code.")
    suite.addTests(load_tests_from_class(TestKMeans))
    suite.addTests(load_tests_from_class(TestDBScan))
    return suite


def suite_not_grouped():
    suite = BitBotsTestSuite("Ungrouped Tests", "Test Cases that are not yet grouped into a suite.")
    suite.addTests(load_tests_from_class(TestMotorConnectionAnalyser))
    suite.addTests(load_tests_from_class(TestLineMatcher))
    return suite

