#-*- coding:utf-8 -*-
"""
LocalWorldModelModule
^^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
''''''''

* 05.04.14: Created (sheepy)

* 06.08.14 Refactor (Marc Bestmann)

* ?????? revert by Martin
"""
from bitbots.modules.abstract.abstract_module import AbstractModule, debug_m
from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME, DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO\
    , DATA_KEY_GOAL_MODEL, DATA_KEY_BALL_FOUND, DATA_KEY_OBSTACLE_INFO, \
    DATA_KEY_OBSTACLE_FOUND, DATA_KEY_BALL_INFO, DATA_KEY_BALL_INFO_FILTERED

from bitbots.modules.basic.worldmodel.local_goal_model_module import convert_polar2uv


class LocalWorldModelModule(AbstractModule):
    def __init__(self):
        pass

    def start(self, data):
        self.i = 0
        pass

    def publish_goal_info(self, data):
        # Goal Info Part
        debug_m(3, "GoalFound", data[DATA_KEY_GOAL_FOUND])
        if data[DATA_KEY_GOAL_FOUND]:
            goal_info = data[DATA_KEY_GOAL_INFO]

            debug_m(3, DATA_KEY_GOAL_INFO + ".1.u", goal_info[0].u)
            debug_m(3, DATA_KEY_GOAL_INFO + ".1.v", goal_info[0].v)

            if len(goal_info.keys()) == 2:
                debug_m(3, DATA_KEY_GOAL_INFO + ".2.u", goal_info[1].u)
                debug_m(3, DATA_KEY_GOAL_INFO + ".2.v", goal_info[1].v)
                #if data[DATA_KEY_RELATIVE_TO_GOAL_POSITION_AVERAGED] is not None:
                #    debug_m(3, "PositionAveraged.x", data[DATA_KEY_RELATIVE_TO_GOAL_POSITION_AVERAGED][0])
                #    debug_m(3, "PositionAveraged.y", data[DATA_KEY_RELATIVE_TO_GOAL_POSITION_AVERAGED][1])
            else:
                debug_m(3, DATA_KEY_GOAL_INFO + ".2.u", 0)
                debug_m(3, DATA_KEY_GOAL_INFO + ".2.v", 0)

        # local GoalModel
        goal_model = data[DATA_KEY_GOAL_MODEL]
        for i in range(4):
            u, v = convert_polar2uv(goal_model.goal_posts[i].distance, goal_model.goal_posts[i].angel)
            debug_m(3, "GoalModel.%d.u" % i, u)
            debug_m(3, "GoalModel.%d.v" % i, v)


    def publish_ball_info(self, data):
        # Ball Info Part
        debug_m(3, "BallFound", data[DATA_KEY_BALL_FOUND])
        if data[DATA_KEY_BALL_FOUND]:
            u, v, x, y, radius, rating, distance = data[DATA_KEY_BALL_INFO]
            debug_m(3, "Ballinfo.x", x)
            debug_m(3, "Ballinfo.y", y)
            debug_m(3, "Ballinfo.u", u)
            debug_m(3, "Ballinfo.v", v)
            debug_m(3, "Ballinfo.Distance", distance)

    def publish_ball_info_prediction(self, data):
        upred, vpred = data[DATA_KEY_BALL_INFO_FILTERED]["uvprediction"]
        if upred:  #  wenn das None ist geht das nicht
            debug_m(3, "Ballinfo.Prediction.u", upred)
            debug_m(3, "Ballinfo.Prediction.v", vpred)


    def publish_obstacle_info(self, data):
        debug_m(3, "ObstacleFound", data[DATA_KEY_OBSTACLE_FOUND])

        # Send the first 5 obstacles

        if data[DATA_KEY_OBSTACLE_FOUND]:
            obstacles = data[DATA_KEY_OBSTACLE_INFO]

            for i in range(5):
                if i < len(obstacles):
                    u, v, x, y, h, w, colour = obstacles[i]
                    debug_m(3, "ObstacleInfo.%i.u" % i, u)
                    debug_m(3, "ObstacleInfo.%i.v" % i, v)
                    debug_m(3, "ObstacleInfo.%i.colour" % i, colour)

    def update(self, data):

        if not data[DATA_KEY_IS_NEW_FRAME]:
            return -1
        if self.i < 10:
            self.i += 1
            return
        self.i = 11
        #self.publish_ball_info(data)
        #self.publish_goal_info(data)
        self.publish_ball_info_prediction(data)
        #self.publish_obstacle_info(data)
        debug_m(3, "draw", 1)


def register(ms):
    ms.add(LocalWorldModelModule, "LocalWorldModel",
           requires=[DATA_KEY_IS_NEW_FRAME,
                     DATA_KEY_BALL_INFO_FILTERED,
                     DATA_KEY_BALL_FOUND,
                     DATA_KEY_BALL_INFO,
                     DATA_KEY_GOAL_FOUND,
                     DATA_KEY_GOAL_INFO,
                     DATA_KEY_OBSTACLE_FOUND,
                     DATA_KEY_OBSTACLE_INFO,
                     DATA_KEY_GOAL_MODEL],
           provides=[])
