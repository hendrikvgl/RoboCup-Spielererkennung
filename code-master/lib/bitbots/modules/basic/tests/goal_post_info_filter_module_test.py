#-*- coding:utf-8 -*-
import random
import unittest
import math
import time

from bitbots.modules.basic.postprocessing.goal_post_info_filter_module import GoalPostInfoDataFilterModule
from bitbots.modules.basic.vision.vision_objects import GoalInfo
from bitbots.modules.keys import DATA_KEY_GOAL_FOUND, DATA_KEY_IS_NEW_FRAME, \
    DATA_KEY_GOAL_INFO, DATA_KEY_RELATIVE_TO_GOAL_POSITION, DATA_KEY_RELATIVE_TO_GOAL_POSITION_AVERAGED


VIEW_PLOTS = False

class TestGoalPostInfoDataFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print "#### Test TestGoalPostInfoDataFilter ####"

    def test_no_processing_on_no_goal_found(self):
        # Setup Data and Module under Test as well as call start
        data = {
            DATA_KEY_GOAL_FOUND: True,
            DATA_KEY_IS_NEW_FRAME: False
        }

        gpidfm = GoalPostInfoDataFilterModule()
        gpidfm.start(data)

        result = gpidfm.update(data)

        self.assertEqual(0, result)

    def test_no_processing_on_no_new_frame_found(self):
        # Setup Data and Module under Test as well as call start
        data = {
            DATA_KEY_GOAL_FOUND: False,
            DATA_KEY_IS_NEW_FRAME: True
        }

        gpidfm = GoalPostInfoDataFilterModule()
        gpidfm.start(data)

        result = gpidfm.update(data)

        self.assertEqual(1, result)

    def test_k_means_with_goal_data_gathered_independently(self):
        # Setup Data and Module under Test as well as call start
        data = {
            DATA_KEY_GOAL_FOUND: True,
            DATA_KEY_IS_NEW_FRAME: True
        }

        gpidfm = GoalPostInfoDataFilterModule()
        gpidfm.start(data)

        if VIEW_PLOTS:

            for i in range(400):
                if random.random() > 0.9:
                    gp1u, gp1v = self.gauss(1875, 500), self.gauss(3250, 500)
                else:
                    gp1u, gp1v = self.gauss(4125, 500), self.gauss(3250, 500)

                data[DATA_KEY_GOAL_INFO] = {
                    0: GoalInfo(0, 0, gp1u, gp1v)
                }

                gpidfm.update(data)
                time.sleep(0.02)

                if i % 200 == 0:
                    x1, y1 = data["Centroids"][0]
                    x2, y2 = data["Centroids"][1]

                    us = [e[0] for e in gpidfm.k_means_list]
                    vs = [e[1] for e in gpidfm.k_means_list]

                    import matplotlib.pyplot as plt

                    plt.plot(us, vs, "bo", linewidth=2)
                    plt.plot(x1, y1, "rs", linewidth=3)
                    plt.plot(x2, y2, "gs", linewidth=3)
                    plt.axis('equal')
                    plt.show()


            time.sleep(0.2)

            for i in range(400):
                if random.random() > 0.9:
                    gp1u, gp1v = self.gauss(4000, 200), self.gauss(-1135, 200)
                else:
                    gp1u, gp1v = self.gauss(4000, 200), self.gauss(1135, 200)

                data[DATA_KEY_GOAL_INFO] = {
                    0: GoalInfo(0, 0, gp1u, gp1v)
                }

                gpidfm.update(data)
                time.sleep(0.02)

                if i % 200 == 0:
                    x1, y1 = data["Centroids"][0]
                    x2, y2 = data["Centroids"][1]

                    us = [e[0] for e in gpidfm.k_means_list]
                    vs = [e[1] for e in gpidfm.k_means_list]

                    import matplotlib.pyplot as plt

                    plt.plot(us, vs, "bo", linewidth=2)
                    plt.plot(x1, y1, "rs", linewidth=3)
                    plt.plot(x2, y2, "gs", linewidth=3)
                    plt.axis('equal')
                    plt.show()

    def gauss(self, mu, sigma):
        return random.gauss(mu, sigma)

    def goal_info_plus_gaussian(self, data, gp1, gp2, noisea, noiseb):
        gp1u, gp1v = self.gauss(gp1[0], noisea), self.gauss(gp1[1], noisea)
        gp2u, gp2v = self.gauss(gp2[0], noiseb), self.gauss(gp2[1], noiseb)

        data[DATA_KEY_GOAL_INFO] = {
            0: GoalInfo(0, 0, gp1u, gp1v),
            1: GoalInfo(0, 0, gp2u, gp2v)
        }
        return (gp1u, gp1v), (gp2u, gp2v)

    def a(self, data, gpidfm, gp1uv, gp2uv, real_pos):
        result = []
        inp = []
        averaged = []
        for i in range(100):
            inp_sample = self.goal_info_plus_gaussian(data, gp1uv, gp2uv, 500, 500)
            inp.append(inp_sample)
            gpidfm.update(data)
            result.append(data[DATA_KEY_RELATIVE_TO_GOAL_POSITION])
            averaged.append(data[DATA_KEY_RELATIVE_TO_GOAL_POSITION_AVERAGED])

        if VIEW_PLOTS:
            import matplotlib.pyplot as plt

            real_pos_x, real_pos_y = real_pos

            # Draw the measured u value for this point in time
            up1 = [e[0][0] + real_pos_x for e in inp]
            vp1 = [e[0][1] + real_pos_y for e in inp]

            up2 = [e[1][0] + real_pos_x for e in inp]
            vp2 = [e[1][1] + real_pos_y for e in inp]

            real_x_estimate = [e[0] for e in result]
            real_y_estimate = [e[1] for e in result]

            real_x_estimate_avrg = [e[0] for e in averaged]
            real_y_estimate_avrg = [e[1] for e in averaged]

            fig = plt.gcf()
            plt.plot(up1, vp1, "yx", linewidth=2)
            plt.plot(up2, vp2, "yx", linewidth=2)

            up1_r = [e[0][0] for e in inp]
            vp1_r = [e[0][1] for e in inp]

            up2_r = [e[1][0] for e in inp]
            vp2_r = [e[1][1] for e in inp]

            for i in range(len(up1)):
                r1 = math.sqrt(up1_r[i] ** 2 + vp1_r[i] ** 2)
                r2 = math.sqrt(up2_r[i] ** 2 + vp2_r[i] ** 2)
                circle1 = plt.Circle((-1135, 4000), r1, color='g', clip_on=False, fill=False)
                circle2 = plt.Circle(( 1135, 4000), r2, color='g', clip_on=False, fill=False)
                fig.gca().add_artist(circle1)
                fig.gca().add_artist(circle2)

            plt.plot(real_x_estimate, real_y_estimate, "bo", linewidth=2)
            plt.plot(real_x_estimate_avrg, real_y_estimate_avrg, "rx", linewidth=2)
            plt.ylim([-100, 4100])
            plt.xlim([-3100, 3100])
            plt.show()

    def a_test_gaussian_distribution_works(self):
        # Setup Data and Module under Test as well as call start
        data = {
            DATA_KEY_GOAL_FOUND: True,
            DATA_KEY_IS_NEW_FRAME: True,
        }

        gpidfm = goal_post_info_filter_module()
        gpidfm.start(data)

        # Standing on the Side of field
        self.a(data, gpidfm, (1875, 3250), (4125, 3250), (-3000, 750))

        # Standing on Center of field - right side
        self.a(data, gpidfm, (-1135, 4000), (1135, 4000), (0, 0))

        # Standing on Center of field - facing to the goal
        self.a(data, gpidfm, (4000, -1135), (4000, -1135), (0, 0))

        # Standing on Center of field - facing to the goal
        e, f = self.get_u_v((350, 790))
        self.a(data, gpidfm, e, f, (350, 790))

    def get_u_v(self, position, angle=0):
        x1,y1,x2,y2 = -1135, 4000, 1135, 4000

        x, y = position

        u1 = x1 - x
        v1 = y1 - y

        u2 = x2 - x
        v2 = y2 - y

        return (u1, v1), (u2, v2)




if __name__ == '__main__':
    unittest.main()