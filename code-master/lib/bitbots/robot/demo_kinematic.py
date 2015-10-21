#!/usr/bin/python

import numpy as np
import time
import sys
from math import cos, sin

from bitbots.robot.kinematics import Robot, KinematicTask
from bitbots.ipc.ipc import SharedMemoryIPC
from bitbots.robot.pypose import PyPose
from bitbots.util import get_config
from bitbots.util.animation import play_animation

config = get_config()
ipc = SharedMemoryIPC()
robot = Robot()
task = KinematicTask(robot)
pose = ipc.get_pose()
#pose = PyPose()
robot.update(pose)
root = 0
r_end_joint = 34
l_end_joint = 35
angle_task_joints = [15, 16]
ignore_joints = [7, 8, 17, 18]

def update(ipc, robot, id=-1, time=0.0):
    pose = ipc.get_pose()
    robot.set_angles_to_pose(pose, id, time)
    ipc.update(pose)

iteration_time = 0.25
steptime = 0.005

if __name__ == "__main__":
    args=sys.argv
    if len(args) > 1:
        play_animation(args[1])
        sleep(2)
        robot.update(ipc.get_pose())
    #Radius in mm
    factor = 45
    #Kreismittelpunkt
    z_offset = 0
    if config["RobotTypeName"] == "Hambot":
        z_offset = 300
    #base_target = np.array((170, 90, -30))
    r_y = robot.get_joint_by_id(r_end_joint).get_endpoint()[1]
    l_y = robot.get_joint_by_id(l_end_joint).get_endpoint()[1]
    r_base_target = np.array((10, r_y, -290 - z_offset))
    l_base_target = np.array((10, l_y, -290 - z_offset))
    r_chain = task.create_chain(root, r_end_joint, (0, 3), angle_task_joints, ignore_joints)
    l_chain = task.create_chain(root, l_end_joint, (0, 3), angle_task_joints, ignore_joints)
    for i in range(10000):
        #local calculating stuff
        begin = time.time()
        current = begin
        end = begin + iteration_time
        dt = 0
        ## local stuff end
        while current < end:
            phase = current / float(iteration_time) * 2 * 3.14159625358
            target_diff = np.array((1.5 * factor * (cos(phase)), 0, -factor * (sin(phase))))
            r_target = r_base_target + target_diff
            l_target = l_base_target - target_diff
            #print r_target
            #robot.inverse_chain(4, target, 1e-3, 100)
            #task.perform(root, l_end_joint, [(1, 0, 0), l_target], (1e-2, 1), (0, 3), 100, angle_task_joints, ignore_joints)
            task.perform_h(r_chain, [(1, 0, 0), r_target], (1e-2, 1), (0, 3), 100)
            task.perform_h(l_chain, [(1, 0, 0), l_target], (1e-2, 1), (0, 3), 100)
            update(ipc, robot, -1, steptime)
            dt = time.time() - current
            current = current + dt
            time.sleep(max(0, steptime - dt))
