# -*- coding:utf-8 -*-
"""
BehaviourModule
^^^^^^^^^^^^^^^

.. moduleauthor:: Martin Poppinga <1popping@informatik.uni-hamburg.de>

History:
* 11.12.13: Created (Martin Poppinga)

Startet das Verhalten
"""
from bitbots.modules.abstract.stack_machine_module import StackMachineModule
from bitbots.modules.behaviour.body.actions.wait import Wait
from bitbots.modules.behaviour.body.decisions.common.duty_decider import DutyDecider
from bitbots.modules.keys import DATA_KEY_BASELINE_INTERSECTION_DISTANCE, DATA_KEY_BASELINE_INTERSECTION_TIME, \
    DATA_KEY_GOAL_MODEL, DATA_KEY_FIELDIE_BALL_TIME_LIST, DATA_KEY_BALL_INFO_FILTERED, DATA_KEY_PENALTY, \
    DATA_KEY_MINIMAL_BALL_TIME, DATA_KEY_GOALIE_BALL_RELATIVE_POSITION, \
    DATA_KEY_BALL_SPEED, \
    DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, DATA_KEY_IPC, DATA_KEY_POSE, DATA_KEY_WALKING, \
    DATA_KEY_BALL_INFO_SIMPLE_FILTERED, DATA_KEY_OBSTACLE_INFO, DATA_KEY_OBSTACLE_FOUND, \
    DATA_KEY_GOAL_INFO_FILTERED, DATA_KEY_HORIZON_OBSTACLES, DATA_KEY_ABSOLUTE_POSITION
from bitbots.modules.keys.grid_world_keys import DATA_KEY_OWN_POSITION_GRID
from bitbots.modules.events import EVENT_MANUAL_START


class BehaviourModule(StackMachineModule):
    def __init__(self):
        self.set_start_module(DutyDecider)

    def start(self, data):
        super(BehaviourModule, self).start(data)
        self.register_to_event(EVENT_MANUAL_START, self.manual_start)

    def manual_start(self, _):
        """ Hält das verhalten für 20 sekunden an"""
        self.interrupt()
        self.push(Wait, 20)


def register(ms):
    ms.add(BehaviourModule, "BehaviourModule",
           requires=[DATA_KEY_IPC, DATA_KEY_BALL_INFO, DATA_KEY_POSE, DATA_KEY_BALL_FOUND,
                     "OwnKickOff", DATA_KEY_PENALTY, DATA_KEY_WALKING, DATA_KEY_BALL_SPEED,
                     DATA_KEY_GOALIE_BALL_RELATIVE_POSITION, DATA_KEY_FIELDIE_BALL_TIME_LIST,
                     DATA_KEY_MINIMAL_BALL_TIME, DATA_KEY_BASELINE_INTERSECTION_DISTANCE,
                     DATA_KEY_BASELINE_INTERSECTION_TIME,
                     DATA_KEY_GOAL_MODEL, DATA_KEY_OBSTACLE_INFO,
                     DATA_KEY_OBSTACLE_FOUND, DATA_KEY_HORIZON_OBSTACLES],
           provides=["Duty"])
