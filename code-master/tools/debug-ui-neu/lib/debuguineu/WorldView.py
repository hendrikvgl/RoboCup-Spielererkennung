#-*- coding:utf-8 -*-
"""
WorldView
^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 5/5/14: Created (sheepy)

"""
import cv2
import numpy as np

from debuguineu.VisionView import VisionView
from bitbots.modules.basic.vision.vision_module import OBSTACLE_UNKNOWN, OBSTACLE_ONLY_MAGENTA, OBSTACLE_CYAN, OBSTACLE_ONLY_CYAN, OBSTACLE_ONLY_COLOR, OBSTACLE_MAGENTA


class WorldView(VisionView):
    def __init__(self, data_callback, view_calback):
        super(WorldView, self).__init__(data_callback, view_calback, "World View")
        #self.make_callbacks("glados")
        self.objectdict = {}
        self.buffer_length = 20
        self.steps = 255 / self.buffer_length
        self.unit_translation = 1E-3
        self.scale_factor = 50 #50
        self.num_meters = 10 #10
        self.colours = {
            OBSTACLE_UNKNOWN: (255, 255, 255),
            OBSTACLE_MAGENTA: (100, 200 , 0),
            OBSTACLE_ONLY_MAGENTA: (55, 150 , 0),
            OBSTACLE_CYAN: (255, 0 , 255),
            OBSTACLE_ONLY_CYAN: (255, 0 , 0),
            OBSTACLE_ONLY_COLOR: (255, 255 , 0)
        }

    def bind_obstacle_fkt(self, robot, i):
        self.make_simple_callback(robot, "Vision.Obstacle.%i.u" % i, "ObstacleInfo.%i.u" % i)
        self.make_simple_callback(robot, "Vision.Obstacle.%i.v" % i, "ObstacleInfo.%i.v" % i)
        self.make_simple_callback(robot, "LocalWorldModel.ObstacleInfo.%i.colour" % i, "ObstacleInfo.%i.colour" % i)

    def make_list_callback(self, robot, income, outcome):
        self.data_callback(
            "%s::Module.%s" % (robot, income),
            lambda item: self.set_info_list(robot, outcome, item.value)
        )

    def make_simple_callback(self, robot, income, outcome):
        self.data_callback(
            "%s::Module.%s" % (robot, income),
            lambda item: self.set_info(robot, outcome, item.value)
        )

    def make_callbacks(self, robot):
        self.make_simple_callback(robot, "Ball.BallFound", "BallFound")
        self.make_list_callback(robot, "BallSimpleFiltered.u", "Ball.u")
        self.make_list_callback(robot, "BallSimpleFiltered.v", "Ball.v")
        self.make_list_callback(robot, "LocalWorldModel.Ballinfo.Prediction.u", "Ballinfo.Prediction.u")
        self.make_list_callback(robot, "LocalWorldModel.Ballinfo.Prediction.v", "Ballinfo.Prediction.v")

        # Data of seen goals
        self.make_simple_callback(robot, "LocalWorldModel.GoalFound", "GoalFound")
        self.make_list_callback(robot, "Vision.GoalPost1.u", "GoalInfo.1.u")
        self.make_list_callback(robot, "Vision.GoalPost1.v", "GoalInfo.1.v")
        self.make_list_callback(robot, "Vision.GoalPost2.u", "GoalInfo.2.u")
        self.make_list_callback(robot, "Vision.GoalPost2.v", "GoalInfo.2.v")

        # LocalGoal Model Data
        self.make_simple_callback(robot, "LocalGoalModel.EnemyGoal.post1u", "GoalModel.0.u")
        self.make_simple_callback(robot, "LocalGoalModel.EnemyGoal.post1v", "GoalModel.0.v")
        self.make_simple_callback(robot, "LocalGoalModel.EnemyGoal.post2u", "GoalModel.1.u")
        self.make_simple_callback(robot, "LocalGoalModel.EnemyGoal.post2v", "GoalModel.1.v")
        self.make_simple_callback(robot, "LocalGoalModel.OwnGoal.post1u", "GoalModel.2.u")
        self.make_simple_callback(robot, "LocalGoalModel.OwnGoal.post1v", "GoalModel.2.v")
        self.make_simple_callback(robot, "LocalGoalModel.OwnGoal.post2u", "GoalModel.3.u")
        self.make_simple_callback(robot, "LocalGoalModel.OwnGoal.post2v", "GoalModel.3.v")

        self.data_callback(
            "%s::Module.LocalWorldModel.draw" % robot,
            lambda item: self.draw(robot)
        )

        self.make_simple_callback(robot, "Vision.ObstacleFound", "ObstacleFound")
        self.bind_obstacle_fkt(robot, 0)
        self.bind_obstacle_fkt(robot, 1)
        self.bind_obstacle_fkt(robot, 2)
        self.bind_obstacle_fkt(robot, 3)
        self.bind_obstacle_fkt(robot, 4)


    def set_info(self, robot, key, value):
        if not robot in self.objectdict:
            self.objectdict[robot] = {}
        self.objectdict[robot][key] = value

    def set_info_list(self, robot, key, value):
        if not robot in self.objectdict:
            self.objectdict[robot] = {}
        if not key in self.objectdict[robot]:
            self.objectdict[robot][key] = []
        self.objectdict[robot][key].append(value)

        if len(self.objectdict[robot][key]) > self.buffer_length:
            self.objectdict[robot][key] = self.objectdict[robot][key][1:]

    def get_colour_intensity(self, i):
        return max(50, i*self.steps)

    def plot_ball_on_field(self, img, robot):
        #draw ball
        found = self.objectdict[robot].get("BallFound", False)
        ball_u_list = self.objectdict[robot].get("Ball.u", [])
        ball_v_list = self.objectdict[robot].get("Ball.v", [])
        assert len(ball_u_list) == len(ball_v_list)

        for i in range(len(ball_u_list)):
            u = ball_u_list[i] * self.unit_translation
            v = ball_v_list[i] * self.unit_translation
            cv2.circle(
                img,
                (int(v * self.scale_factor* -1) + 500, int(u * self.scale_factor * -1) + 500),
                2,
                (0, self.get_colour_intensity(i)/2, self.get_colour_intensity(i)) if found else (100, 100, 100),
                3)

    def plot_obstacle_info_on_field(self, img , robot):
        #draw ball
        obstacleFound = self.objectdict[robot].get("ObstacleFound", False)

        if obstacleFound:
            for i in range(5):
                u = self.objectdict[robot].get("ObstacleInfo.%i.u" % i, -10) * self.unit_translation
                v = self.objectdict[robot].get("ObstacleInfo.%i.v" % i, -10) * self.unit_translation
                col = self.objectdict[robot].get("ObstacleInfo.%i.colour" % i, OBSTACLE_UNKNOWN)
                c = self.colours[col]
                cv2.circle(
                img,
                (int(v * self.scale_factor* -1) + 500, int(u * self.scale_factor * -1) + 500),
                2,
                c,
                3)


    def plot_ball_prediction_on_field(self, img, robot):
        #draw ball
        ball_u_list = self.objectdict[robot].get("Ballinfo.Prediction.u", [])
        ball_v_list = self.objectdict[robot].get("Ballinfo.Prediction.v", [])
        assert len(ball_u_list) == len(ball_v_list)

        for i in range(len(ball_u_list)):
            u = ball_u_list[i] * self.unit_translation
            v = ball_v_list[i] * self.unit_translation
            cv2.circle(
                img,
                (int(v * self.scale_factor* -1) + 500, int(u * self.scale_factor * -1) + 500),
                2,
                (0, 0, self.get_colour_intensity(i)),
                3)

    def draw_field_circles(self):
        img = np.zeros((1000, 1000, 4), np.uint8)
        #img.fill(255)
        for i in range(0, self.num_meters):
            cv2.circle(
                img,
                (500, 500),
                i * self.scale_factor,
                (155, 155, 155))
        cv2.line(
            img,
            (500, 0),
            (500, 1000),
            (255, 255, 255))
        cv2.line(
            img,
            (0, 500),
            (1000, 500),
            (255, 255, 255))
        return img

    def plot_goal_on_field(self, img, robot):
        found_goal = self.objectdict[robot].get("GoalFound", False)
        goal_u_1_list = self.objectdict[robot].get("GoalInfo.1.u", [])
        goal_v_1_list = self.objectdict[robot].get("GoalInfo.1.v", [])
        goal_u_2_list = self.objectdict[robot].get("GoalInfo.2.u", [])
        goal_v_2_list = self.objectdict[robot].get("GoalInfo.2.v", [])

        assert len(goal_u_1_list) == len(goal_v_1_list)
        assert len(goal_u_2_list) == len(goal_v_2_list)

        if found_goal:

            for i in range(len(goal_u_1_list)):
                u = goal_u_1_list[i] * self.unit_translation
                v = goal_v_1_list[i] * self.unit_translation
                ci = self.get_colour_intensity(i)
                cv2.circle(
                    img,
                    (int(v * self.scale_factor* -1) + 500, int(u * self.scale_factor * -1) + 500),
                    2,
                    (0, ci, ci),
                    3)

            for i in range(len(goal_u_2_list)):
                u = goal_u_2_list[i] * self.unit_translation
                v = goal_v_2_list[i] * self.unit_translation
                ci = self.get_colour_intensity(i)
                cv2.circle(
                    img,
                    (int(v * self.scale_factor * -1) + 500, int(u * self.scale_factor * -1) + 500),
                    2,
                    (0, ci, ci),
                    3)

        for i in range(4):
            u = self.objectdict[robot].get("GoalModel.%d.u" % i, 0) * self.unit_translation
            v = self.objectdict[robot].get("GoalModel.%d.v" % i, 0) * self.unit_translation
            print "GoalModel: ", i, u, v
            cv2.circle(
                    img,
                    (int(v * self.scale_factor* -1) + 500, int(u * self.scale_factor * -1) + 500),
                    2,
                    (255, 0, 0),
                    3)

    def draw(self, robot):
        img = self.draw_field_circles()
        self.plot_ball_on_field(img, robot)
        #self.plot_ball_prediction_on_field(img, robot)
        self.plot_goal_on_field(img, robot)
        self.plot_obstacle_info_on_field(img, robot)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_min = cv2.resize(img, (0, 0), fx=self.FACTOR2, fy=self.FACTOR2)
        #rgbimage = cv2.cvtColor(img,cv2.cv.CV_BGR2RGB)
        #print "Call draw"
        self.show_image(img_min, img, robot)
