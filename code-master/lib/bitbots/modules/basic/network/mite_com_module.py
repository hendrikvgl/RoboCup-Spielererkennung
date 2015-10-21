#-*- coding:utf-8 -*-
"""
MiteComModule
^^^^^^^^^^^^^

This module provides team- and inter-team communication. I uses the Mitecom protocoll.

Configfile: config/mitecom.yaml

History:
''''''''

* 07.03.14: Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

import time

from mitecom.mitecom import MiteCom
from mitecom.mitecom import STATE_ACTIVE, STATE_PENALIZED, ROLE_OTHER
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.events import EVENT_PENALTY, EVENT_NO_PENALTY
from bitbots.modules.abstract import AbstractThreadModule
from bitbots.modules.keys import DATA_KEY_TEAM_MATES, DATA_KEY_BALL_TIME, DATA_KEY_KICKOFF_OFFENSE_SIDE, DATA_KEY_DUTY
from bitbots.modules.keys import DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO
from bitbots.modules.keys import DATA_KEY_ROLE, DATA_KEY_CONFIG
from bitbots.modules.keys.grid_world_keys import DATA_KEY_OPPONENT_ROBOT, DATA_KEY_TEAM_MATE, DATA_KEY_OWN_POSITION_GRID


class MiteComModule(AbstractThreadModule):
    """
    This class does the communication with other robots.
    """

    def __init__(self):
        super(MiteComModule, self).__init__(
            requires=[
                DATA_KEY_CONFIG, DATA_KEY_DUTY, DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO,
                DATA_KEY_BALL_TIME, DATA_KEY_ROLE, DATA_KEY_KICKOFF_OFFENSE_SIDE, DATA_KEY_OPPONENT_ROBOT,
                DATA_KEY_TEAM_MATE, DATA_KEY_OWN_POSITION_GRID],
            provides=[DATA_KEY_TEAM_MATES]
        )
        self.penalty = False
        self.set(DATA_KEY_TEAM_MATES, {})

    def start(self, data):
        super(MiteComModule, self).start(data)
        self.register_to_event(
            EVENT_PENALTY,
            lambda data: self.set_penalty(True))
        self.register_to_event(
            EVENT_NO_PENALTY,
            lambda data: self.set_penalty(False))

    def set_penalty(self, flag):
        self.penalty = flag

    def run(self):
        config = self.get(DATA_KEY_CONFIG)
        mitecom = MiteCom(
            int(config['mitecom']['port']),
            int(config["TEAM"]))
        mitecom.set_robot_id(int(config["PLAYER"]))
        lastsend = time.time()
        while True:
            if not config['mitecom']['enabled']:
                # momentan nicht aktiv, wir schlafen
                time.sleep(1)
                continue
            if time.time() - lastsend > 0.25:
                lastsend = time.time()
                if self.penalty:
                    mitecom.set_state(STATE_PENALIZED)
                else:
                    mitecom.set_state(STATE_ACTIVE)
                mitecom.set_role(self.get(DATA_KEY_ROLE, ROLE_OTHER))
                if self.get(DATA_KEY_BALL_FOUND) and not self.penalty:
                    ball = self.get(DATA_KEY_BALL_INFO)
                    mitecom.set_relative_ball(
                        int(ball.u),
                        int(ball.v))
                    # distance to ball in meter
                    # mitecom uses millimeter
                    mitecom.set_ball_time(self.get(DATA_KEY_BALL_TIME))

                if self.get(DATA_KEY_KICKOFF_OFFENSE_SIDE, 0) != 0:
                    offence_side = self.get(DATA_KEY_KICKOFF_OFFENSE_SIDE)
                    mitecom.set_kickoff_offence_side(offence_side)

                if (not reduce(lambda x, y: x and y,
                          map(lambda e1, e2: e1 == e2,
                            self.get(DATA_KEY_OPPONENT_ROBOT, [0, 0, 0, 0, 0, 0, 0, 0]),
                            [0, 0, 0, 0, 0, 0, 0, 0])) \
                        and
                        (not self.penalty)):
                    opponent_robot = self.get(DATA_KEY_OPPONENT_ROBOT)
                    mitecom.set_opponent_robot(opponent_robot)

                if (not reduce(lambda x, y: x and y,
                          map(lambda e1, e2: e1 == e2,
                            self.get(DATA_KEY_TEAM_MATE, [0, 0, 0, 0, 0, 0, 0, 0]),
                            [0, 0, 0, 0, 0, 0, 0, 0]))) \
                        and \
                        (not self.penalty):
                    team_mate = self.get(DATA_KEY_TEAM_MATE)
                    mitecom.set_team_mate(team_mate)

                mitecom.send_data()
            data = mitecom.recv_data()
            if data != {}:
                for robid in data:
                    rob = data[robid]
                    debug_m(3,
                            "robot." + str(rob.get_id()) + ".Role",
                            rob.get_role())
                    debug_m(3,
                            "robot." + str(rob.get_id()) + ".Ball_X",
                            rob.get_relative_ball_x())
                    debug_m(3,
                            "robot." + str(rob.get_id()) + ".Ball_Y",
                            rob.get_relative_ball_y())
                    debug_m(3,
                            "robot." + str(rob.get_id()) + ".Ball_Time",
                            rob.get_ball_time())
            self.set(DATA_KEY_TEAM_MATES, data)
            time.sleep(0.1)


def register(ms):
    ms.add(MiteComModule, "MiteCom",
           requires=[DATA_KEY_CONFIG,
                     DATA_KEY_BALL_INFO,
                     DATA_KEY_BALL_FOUND,
                     DATA_KEY_BALL_TIME],

           provides=[DATA_KEY_TEAM_MATES])
