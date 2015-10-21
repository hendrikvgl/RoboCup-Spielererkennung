#-*- coding:utf-8 -*-
import unittest
from bitbots.modules.basic.vision.vision_objects import BallInfo

from bitbots.modules.keys import DATA_KEY_BALL_INFO, DATA_KEY_BALL_SPEED, DATA_KEY_BALL_VECTOR, \
    DATA_KEY_BASELINE_INTERSECTION_DISTANCE, DATA_KEY_BASELINE_INTERSECTION_TIME
from bitbots.modules.basic.postprocessing.goalie_line_intersection_module import GoalieLineIntersectionModule





class TestGoalieIntersectionModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "#### Test GoalieIntersectModule ####"


    def test_feature_toggle_enabled(self):
        glim = GoalieLineIntersectionModule()

        data = {}
        glim.start(data)

        data[DATA_KEY_BALL_INFO] = BallInfo(0.15, 0.20, None, None, None, None, None)
        data[DATA_KEY_BALL_SPEED] = 10
        data[DATA_KEY_BALL_VECTOR] = (-0.03, -0.05)

        data_return = glim.update(data)

        target_time = data[DATA_KEY_BASELINE_INTERSECTION_TIME]
        target_distance = data[DATA_KEY_BASELINE_INTERSECTION_DISTANCE]

        self.assertEqual(None, data_return)

        msg = "Target Time, Distance %f %f" % (target_time, target_distance)

        self.assertAlmostEqual(5, target_time, delta=10E-5, msg=msg)
        self.assertAlmostEqual(-0.05, target_distance, delta=10E-5, msg=msg)


if __name__ == "__main__":
    unittest.main()
