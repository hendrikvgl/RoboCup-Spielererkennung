#-*- coding:utf-8 -*-
import unittest

from bitbots.modules.basic.postprocessing.ball_speed_module import BallSpeedModule
from bitbots.modules.basic.tests.test_data import uv_for_three_ballmovements_towards_robot
from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME, DATA_KEY_BALL_SPEED, DATA_KEY_BALL_VECTOR, \
    DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, DATA_KEY_BALL_INFO
from bitbots.util.test.PyMock import PyMock
from bitbots.debug import Scope


class TestBallSpeedModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "#### Test BallSpeedModule ####"

    def setUp(self):
        self.bsm = BallSpeedModule()
        debug = Scope("Module")
        self.bsm.internal_init(debug, object)

    def get_default_data(self):
        data = {DATA_KEY_CAMERA_CAPTURE_TIMESTAMP: 0, DATA_KEY_IS_NEW_FRAME: True, "Walking.Active": False,
                "BallFound": True}

        ball_mock = PyMock()
        data[DATA_KEY_BALL_INFO] = ball_mock
        return data

    def test_no_ball_movement(self):
        data = self.get_default_data()
        data["BallInfo"]._setSomething("distance", 0.34)
        data["BallInfo"]._setSomething("u", 0.34)
        data["BallInfo"]._setSomething("v", 0.34)
        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 1

        # Make the first update
        self.bsm.update(data)

        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 2
        self.bsm.update(data)

        # Assert that BallSpeed is 0 because there couldn't be any evaluation with just one distance
        self.assertEquals(0, data[DATA_KEY_BALL_SPEED])

        # Make another Update Call
        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 3
        self.bsm.update(data)

        # With two data points it should be now zero
        self.assertEquals(0, data[DATA_KEY_BALL_SPEED])


    def test_ball_is_moving(self):
        data = self.get_default_data()

        # Set the First Distance
        data["BallInfo"]._setSomething("distance", 0.4)
        data["BallInfo"]._setSomething("u", 0.4)
        data["BallInfo"]._setSomething("v", 0.4)
        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 1
        self.bsm.update(data)

        # Perpare the Mock for the Second Distance
        ballMock = PyMock()
        data["BallInfo"] = ballMock
        data["BallInfo"]._setSomething("distance", 0.5)
        data["BallInfo"]._setSomething("u", 0.5)
        data["BallInfo"]._setSomething("v", 0.4)
        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 2
        self.bsm.update(data)

        self.assertAlmostEquals(0.1, data[DATA_KEY_BALL_SPEED])
        self.assertAlmostEquals(0.1, data[DATA_KEY_BALL_VECTOR][0])

        # Perpare the Mock for the Third Distance
        ballMock = PyMock()
        data["BallInfo"] = ballMock
        data["BallInfo"]._setSomething("distance", 0.3)
        data["BallInfo"]._setSomething("u", 0.3)
        data["BallInfo"]._setSomething("v", 0.4)
        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 3
        self.bsm.update(data)

        # Assert that speed is 0.2 and positive
        self.assertAlmostEquals(0.2, data[DATA_KEY_BALL_SPEED])
        self.assertAlmostEquals(-0.2, data[DATA_KEY_BALL_VECTOR][0])


    def test_ball_speed_behaviour(self):
        us = uv_for_three_ballmovements_towards_robot["u"]
        vs = uv_for_three_ballmovements_towards_robot["v"]

        data = {}

        self.bsm = BallSpeedModule()
        self.bsm.start(data)

        ball_speed = []
        ball_vector = []

        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = 0
        data[DATA_KEY_IS_NEW_FRAME] = True
        data["Walking.Active"] = False
        data["BallFound"] = True
        data[DATA_KEY_BALL_INFO] = PyMock()
        data[DATA_KEY_BALL_INFO]._setSomething("u", 0.3)
        data[DATA_KEY_BALL_INFO]._setSomething("v", 0.4)

        for i in range(len(us)):
            u, v = us[i], vs[i]
            data[DATA_KEY_BALL_INFO]._setSomething("u", u)
            data[DATA_KEY_BALL_INFO]._setSomething("v", v)
            data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = i / 20.0

            self.bsm.update(data)

            ball_speed.append(data[DATA_KEY_BALL_SPEED])
            ball_vector.append(data[DATA_KEY_BALL_VECTOR])

        if False:
            import matplotlib.pyplot as plt

            # Draw the measured u value for this point in time
            plt.plot(range(len(ball_speed)), ball_speed, 'r-', linewidth=2)

            plt.show()


if __name__ == '__main__':
    unittest.main()
