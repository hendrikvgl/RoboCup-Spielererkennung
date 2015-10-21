#-*- coding:utf-8 -*-
"""
ValidateLocalGoalModelModule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prüft mit Goalie Informationen, ob der Roboter das Goalmodel richtig rum hat und korrigiert es ggf.

History:
''''''''

* created 17.7.14 (Martin Poppinga, Marc Bestmann)

* 06.08.14 Refactor (Marc Bestmann)


"""
import math

from bitbots.modules.abstract.abstract_module import AbstractModule
from bitbots.modules.keys import DATA_KEY_BALL_INFO, DATA_KEY_GOALIE_BALL_RELATIVE_POSITION, DATA_KEY_IS_NEW_FRAME, \
    DATA_KEY_GOAL_MODEL, DATA_KEY_BALL_FOUND
from bitbots.util.config import get_config


config = get_config()['field']
length = config['length']


class ValidateLocalGoalModelModule(AbstractModule):
    def update(self, data):
        if data[DATA_KEY_IS_NEW_FRAME] and data[DATA_KEY_BALL_FOUND] and data.get(DATA_KEY_GOALIE_BALL_RELATIVE_POSITION, 0) != 0:
            ball_distance = data[DATA_KEY_BALL_INFO].distance
            if ball_distance < 1000:  # TODO config

                own_goal_distance = data[DATA_KEY_GOAL_MODEL].get_own_goal()
                opp_goal_distance = data[DATA_KEY_GOAL_MODEL].get_opp_goal()

                goalie_ball_distance = math.sqrt(
                    data[DATA_KEY_GOALIE_BALL_RELATIVE_POSITION][0] ** 2
                    + data[DATA_KEY_GOALIE_BALL_RELATIVE_POSITION][1] ** 2)

                delta_opp_goalie_ball = abs(opp_goal_distance - goalie_ball_distance)
                delta_own_goalie_ball = abs(own_goal_distance - goalie_ball_distance)

                if goalie_ball_distance < length / 2 - 500:
                    if delta_opp_goalie_ball < delta_own_goalie_ball:
                        data[DATA_KEY_GOAL_MODEL].switch()

                elif goalie_ball_distance > length / 2 + 500:

                    if delta_opp_goalie_ball < delta_own_goalie_ball:
                        data[DATA_KEY_GOAL_MODEL].switch()

                else:
                    pass  # Tu Nichts weil genau in der Mitte


def register(ms):
    ms.add(ValidateLocalGoalModelModule, "ValidateLocalGoalModelModule",
           requires=[DATA_KEY_IS_NEW_FRAME,
                     DATA_KEY_GOALIE_BALL_RELATIVE_POSITION,
                     DATA_KEY_BALL_INFO,
                     DATA_KEY_BALL_FOUND,
                     DATA_KEY_GOAL_MODEL,
                     DATA_KEY_GOALIE_BALL_RELATIVE_POSITION],
           #, "Duty"
           provides=[])