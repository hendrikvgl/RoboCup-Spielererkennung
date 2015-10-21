# -*- coding:utf-8 -*-
"""
HeadHelper
^^^^^^^^^^
Hat ein paar methoden die praktisch sind

.. moduleauthor:: Marc Bestmann <0bestman@informatik.uni-hamburg.de>

History:

* 13.12.13: Created (Marc)

"""
import math
from bitbots.ipc.ipc import SharedMemoryIPC
from bitbots.util import get_config
from bitbots.robot.kinematics import Robot, KinematicTask
import numpy as np
from bitbots.util.kinematicutil import get_head_angles_for_distance_with_y_offset

robot = Robot()


def get_pantilt_from_uv(u, v, ipc):
    task = KinematicTask(robot)
    # ipc = SharedMemoryIPC()

    pose = ipc.get_pose()
    robot.update(pose)
    get_head_angles_for_distance_with_y_offset(robot, np.array((u, v)), 1, 0.2)
    robot.set_angles_to_pose(pose)
    pan_tilt = np.array((pose.head_pan.goal, pose.head_tilt.goal))

    return pan_tilt


def look_at_ball_with_offset(connector, pan_offset):
    look_at_with_offset(connector, pan_offset, "Ball")


def look_at_enemy_goal_with_offset(connector, pan_offset):
    look_at_with_offset(connector, pan_offset, "EnemyGoal")


def look_at_own_goal_with_offset(connector, pan_offset):
    look_at_with_offset(connector, pan_offset, "OwnGoal")


def look_at_with_offset(connector, pan_offset, target):
    common_behaviour_config = get_config()["Behaviour"]["Common"]
    pan_speed = common_behaviour_config["Search"]["maxPanSpeedSearch"]
    tilt_speed = common_behaviour_config["Search"]["maxTiltSpeedSearch"]
    max_pan_angle = common_behaviour_config["Camera"]["maxPan"]
    # max angle to look down (must be positive)
    max_down_angle = common_behaviour_config["Camera"]["minTilt"]
    # max angle to look up (must be positive)
    max_up_angle = common_behaviour_config["Camera"]["maxTilt"]

    local_goal_model = connector.filtered_vision_capsule().get_local_goal_model()
    if target == "Ball":
        target_pan, target_tilt = get_pantilt_from_uv(local_goal_model.get_ball_position()[0],
                                                      local_goal_model.get_ball_position()[1])
    elif target == "EnemyGoal":
        target_pan, target_tilt = get_pantilt_from_uv(local_goal_model.get_opp_goal()[0],
                                                      local_goal_model.get_opp_goal()[1])
    elif target == "OwnGoal":
        target_pan, target_tilt = get_pantilt_from_uv(local_goal_model.get_own_goal()[0],
                                                      local_goal_model.get_own_goal()[1])
    else:
        raise ValueError()

    if math.fabs(target_pan + pan_offset) < max_pan_angle:
        target_pan += pan_offset
    elif target_pan + pan_offset < 0:
        target_pan = - max_pan_angle
    else:
        target_pan = max_pan_angle

    if target_tilt > max_up_angle:
        target_tilt = max_up_angle
    elif target_tilt < max_down_angle:
        target_tilt = max_down_angle
    pose = connector.get_pose()
    ipc = connector.get_ipc()

    pose.head_pan.goal = target_pan
    pose.head_tilt.goal = target_tilt
    pose.head_pan.speed = pan_speed
    pose.head_tilt.speed = tilt_speed
    connector.set_pose(pose)
