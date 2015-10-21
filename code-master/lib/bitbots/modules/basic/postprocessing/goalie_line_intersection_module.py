#-*- coding:utf-8 -*-

"""
GoalieLineIntersection Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This module compute from velocity and moving vektor the intersection point with the ground line of the goal.
This should be help for the decision of the goalie.

messured in m and s

History:
''''''''

* 02.04.14: Created (Maike Paetzel)

* 06.08.14 Refactor (Marc Bestmann)
"""
#TODO einheiten überprüfen, im kommentar oben steht m sollte aber mm sein
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_KEY_BASELINE_INTERSECTION_TIME, DATA_KEY_BASELINE_INTERSECTION_DISTANCE, \
    DATA_KEY_BALL_INFO, DATA_KEY_BALL_SPEED, DATA_KEY_BALL_VECTOR


class GoalieLineIntersectionModule(AbstractModule):
    def start(self, data):
        #Initialisation with "NotFound"
        data[DATA_KEY_BASELINE_INTERSECTION_TIME] = -1
        data[DATA_KEY_BASELINE_INTERSECTION_DISTANCE] = -1

    def update(self, data):

        # If no Ball is found there can't be valid data
        if data[DATA_KEY_BALL_SPEED] == -1:
            data[DATA_KEY_BASELINE_INTERSECTION_TIME] = -1
            data[DATA_KEY_BASELINE_INTERSECTION_DISTANCE] = -1
            return

        # If the ball is moving away from the robot
        if data[DATA_KEY_BALL_VECTOR][0] >= 0:
            data[DATA_KEY_BASELINE_INTERSECTION_TIME] = -1
            data[DATA_KEY_BASELINE_INTERSECTION_DISTANCE] = -1
            return

        # Ball is moving towards us
        u = data[DATA_KEY_BALL_INFO].u
        v = data[DATA_KEY_BALL_INFO].v

        delta_u = data[DATA_KEY_BALL_VECTOR][0]
        delta_v = data[DATA_KEY_BALL_VECTOR][1]

        # zeit bis der ball auf der grundline zum roboter ist
        s = - float(u) / delta_u
        # seitliche position des balls wenn er auf der grundline des roboters ankommt
        #dran denken: minus werte sind links positive rechts (wie beim v)
        r = v + s * delta_v

        #a = np.array([[0,1], [delta_u,delta_v]])
        #b = np.array([u,v])
        #solution = np.linalg.solve(a, b)

        data[DATA_KEY_BASELINE_INTERSECTION_TIME] = s
        data[DATA_KEY_BASELINE_INTERSECTION_DISTANCE] = r

        debug_m(3, "GoalieIntersectionTime ", data[DATA_KEY_BASELINE_INTERSECTION_TIME])
        debug_m(3, "GoalieIntersectionDistanc ", data[DATA_KEY_BASELINE_INTERSECTION_DISTANCE])

        return


def register(ms):
    ms.add(GoalieLineIntersectionModule, "GoalieLineIntersectionModule",
           requires=[DATA_KEY_BALL_INFO,
                     DATA_KEY_BALL_VECTOR,
                     DATA_KEY_BALL_SPEED],
           provides=[DATA_KEY_BASELINE_INTERSECTION_TIME,
                     DATA_KEY_BASELINE_INTERSECTION_DISTANCE])
