import unittest
from bitbots.debug.debug_decorator import ComplexObjectConverter
from bitbots.modules.basic.vision.vision_objects import GoalInfo
from bitbots.modules.keys import DATA_KEY_GOAL_INFO

class DebugStub():

    def __init__(self):
        self.called_with = []

    def __call__(self, key, value):
        self.called_with.append([key, value])

    def get_num_elements(self):
        return len(self.called_with)

    def get_list_of_values(self):
        return [e[1] for e in self.called_with]



class TestComplexObjectConverter(unittest.TestCase):

    def test_no_goal_post(self):
        debug_stub = DebugStub()
        ComplexObjectConverter.convert_goal_info(debug_stub, DATA_KEY_GOAL_INFO, None)

        self.assertEqual(0, debug_stub.get_num_elements())

    def test_two_goal_posts(self):
        debug_stub = DebugStub()
        ComplexObjectConverter.convert_goal_info(debug_stub, DATA_KEY_GOAL_INFO, {0: GoalInfo(1, 4, 5, 8, 0, 0),
                                                                                  1: GoalInfo(2, 3, 6, 7, 0, 0)})
        self.assertEqual(4, debug_stub.get_num_elements())
        self.assertEqual(0, len([e for e in debug_stub.get_list_of_values() if e is None]))

    def test_one_goal_post(self):
        debug_stub = DebugStub()
        ComplexObjectConverter.convert_goal_info(debug_stub, DATA_KEY_GOAL_INFO, {0: GoalInfo(1, 4, 5, 8, 0, 0)})

        self.assertEqual(4, debug_stub.get_num_elements())
        self.assertEqual(2, len([e for e in debug_stub.get_list_of_values() if e is None]))
