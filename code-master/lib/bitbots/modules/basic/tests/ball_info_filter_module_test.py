#-*- coding:utf-8 -*-
import time

from bitbots.modules.basic.postprocessing.ball_info_filter_module import BallInfoDataFilterModule
from bitbots.modules.basic.tests.test_data import uv_for_three_ballmovements_towards_robot
from bitbots.util.test.PyMock import PyMock
from bitbots.modules.keys import DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, DATA_KEY_BALL_INFO_FILTERED, DATA_KEY_IS_NEW_FRAME

import unittest


class TestBallInfoDataFilterModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print "#### Test BallSpeedModule ####"

    def setUp(self):
        self.uv_dump = uv_for_three_ballmovements_towards_robot

    def draw_first(self, predictions, us, vs, fig, a, b):
        import matplotlib.pyplot as plt

        # The Prediction Data
        up = [e[0] for e in predictions][a:b]
        vp = [e[1] for e in predictions][a:b]
        vs_f = vs[a:b]
        us_f = us[a:b]
        # The Setup of the figure
        fig = plt.figure(fig)
        ax = fig.add_subplot(111)
        ax.set_title("READ the Comment in Test Class!!!\nBallInfoDataFilterModule")
        ax.set_ylim([-1, 10])
        ax.set_xlim([-1, 10])
        # Plot the Prediction Data
        for i in range(len(vp)):
            cr = (i * 5 / 255.0) % 1
            ax.plot(vp[i], up[i], 'bo', color=(cr, 0, 0), linewidth=1)
            ax.plot(vs_f[i], us_f[i], 'rs', color=(0, cr, 0), linewidth=2)

        # Draw Vertical Lines where the predicted u is below zero
        ax.axvline(x=0, color="y")
        ax.axvline(x=-1, color="g")

        # Draw Horizontal Lines based on u meaning the distance of the ball
        ax.axhline(y=0, color="g", linestyle="-.")


    def test_uv_prediction(self):
        data = {}
        ballMock = PyMock()
        data["BallInfo"] = ballMock
        data["BallFound"] = True
        data[DATA_KEY_IS_NEW_FRAME] = True

        us = [(i/20.0)**3 for i in range(50)]
        vs = [(i/20.0)**2 for i in range(50)]
        time = range(50)

        us = us[0:30] + us[30:50]
        vs = vs[0:30] + vs[30:50]
        time = time[0:30] + time[30:50]

        us[30] = 10

        bidfm = BallInfoDataFilterModule()
        bidfm.start(data)

        predictions = []
        grades = []

        for i in range(len(us)):
            data["BallInfo"]._setSomething("u", us[i])
            data["BallInfo"]._setSomething("v", vs[i])
            data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = time[i]
            # Simplistic counter for increasing time

            # Call the module
            bidfm.update(data)

            self.assertTrue("uvprediction" in data[DATA_KEY_BALL_INFO_FILTERED])

            predictions.append(data[DATA_KEY_BALL_INFO_FILTERED]["uvprediction"])
            grades.append(data[DATA_KEY_BALL_INFO_FILTERED]["uvgrade"])



        if False:
            import matplotlib.pyplot as plt

            self.draw_first(predictions, us, vs, 1, 0, 50)
            # Draw the measured u value for this point in time

            #plt.plot(range(len(grades)), [math.sqrt(e[0]**2+e[1]**2) for e in grades], 'r-')

            # COMMENT - The red dots are the real u values measured,
            # the blue values the estimated values in 5 time steps
            # The green dotted lines are for better reading the u value
            # the Vertical lines describe when the estimation of u in 5 time steps is below zero

            plt.show()

    def test_with_plain_values(self):
        bidfm = BallInfoDataFilterModule()

        t = time.time()

        yu = [1300, 1200, 1100, 1000, 900]
        yv = [0, 10, 30, 45, 65]
        timestamps = [t, t+0.06, t+0.12, t+0.18, t+0.24]
        print "Result", bidfm.calculate_regression(yu, yv, timestamps, look_into_future=0.78)



if __name__ == '__main__':
    unittest.main()


