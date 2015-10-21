#-*- coding:utf-8 -*-
"""
TeamData
^^^^^^^^

This module works with the data that is comming from the team

History:
''''''''

* ??.??.??: Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

* 08.01.15 GridWorld (Judith Hartfill)

"""
import time

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_KEY_TEAM_MATES, DATA_KEY_MINIMAL_BALL_TIME, \
    DATA_KEY_KICKOFF_OFFENSE_SIDE_RECEIVED, DATA_KEY_GOALIE_BALL_RELATIVE_POSITION, DATA_KEY_FIELDIE_BALL_TIME_LIST
from bitbots.modules.keys.grid_world_keys import DATA_KEY_OPPONENT_ROBOT, DATA_KEY_TEAM_MATE, DATA_KEY_OWN_POSITION_GRID
from mitecom.mitecom import STATE_ACTIVE, ROLE_GOALIE
from mitecom.mitecom import MiteCom
from bitbots.util import get_config

config = get_config()

class TeamDataModule(AbstractModule):

    def update(self, data):

        # minimal distance to fieldie
        minimal_ball_walk_time = 99999999999999
        fieldie_ball_time_list = []
        for robot in data[DATA_KEY_TEAM_MATES].itervalues():
            if robot.get_state() == STATE_ACTIVE:
                robot_ball_time = robot.get_ball_time()
                if robot_ball_time:
                    if robot_ball_time < minimal_ball_walk_time:
                        minimal_ball_walk_time = robot_ball_time
                if robot.get_role() == ROLE_GOALIE:
                    # provide distance from goalie to ball
                    data[DATA_KEY_GOALIE_BALL_RELATIVE_POSITION] = (
                        robot.get_relative_ball_x(),
                        robot.get_relative_ball_y())
                    #fieldie_ball_time_list.append((robot.get_id(), robot.get_ball_time())) #%TODO FIELDIE<- bennenung
                else:
                    fieldie_ball_time_list.append((robot.get_id(), robot.get_ball_time()))
                if not robot.get_id() == int(config["PLAYER"]):
                    data[DATA_KEY_OPPONENT_ROBOT] = (
                        robot.get_opponent_robot_x(),
                        robot.get_opponent_robot_y(),
                        robot.get_opponent_robot_3(),
                        robot.get_opponent_robot_4(),
                        robot.get_opponent_robot_5(),
                        robot.get_opponent_robot_6(),
                        robot.get_opponent_robot_7(),
                        robot.get_opponent_robot_8())
                    data[DATA_KEY_TEAM_MATE] = (
                        robot.get_team_mate_x(),
                        robot.get_team_mate_y(),
                        robot.get_team_mate_3(),
                        robot.get_team_mate_4(),
                        robot.get_team_mate_5(),
                        robot.get_team_mate_6(),
                        robot.get_team_mate_7(),
                        robot.get_team_mate_8())
                   # data[DATA_KEY_OWN_POSITION_GRID] = (
                        #robot.get_own_position_grid_x(),
                        #robot.get_own_position_grid_y())
            if robot.get_kickoff_offence_side() != 0:
                debug_m(3, str(robot), robot.get_kickoff_offence_side())
                data[DATA_KEY_KICKOFF_OFFENSE_SIDE_RECEIVED] = (robot.get_kickoff_offence_side(), time.time())
        data[DATA_KEY_MINIMAL_BALL_TIME] = minimal_ball_walk_time
        data[DATA_KEY_FIELDIE_BALL_TIME_LIST] = fieldie_ball_time_list


def register(ms):

    ms.add(TeamDataModule, "TeamData",
           requires=[DATA_KEY_TEAM_MATES],
           provides=[DATA_KEY_MINIMAL_BALL_TIME,
                     DATA_KEY_GOALIE_BALL_RELATIVE_POSITION,
                     DATA_KEY_FIELDIE_BALL_TIME_LIST,
                     DATA_KEY_KICKOFF_OFFENSE_SIDE_RECEIVED])
