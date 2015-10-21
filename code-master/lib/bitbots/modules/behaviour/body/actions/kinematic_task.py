# -*- coding:utf-8 -*-
"""
KinematicTask
^^^^^^^^^^^^^

Does a kinematic Task. Needs as an argument a tupel of an array with the perform arguments of the kinematic task and the
time. If the time is zero, the fastest possible action will be performed.

History:
* 08.12.14: Created (Marc Bestmann)
"""
import time
from bitbots.modules.abstract.abstract_action_module import AbstractActionModule
from bitbots.ipc.ipc import *


class KinematicTask(AbstractActionModule):
    def __init__(self, args):
        super(KinematicTask, self).__init__()
        self.started = False
        self.args = args[0]
        self.time = args[1]
        self.additional_angles = args[2] if len(args) == 3 else None
        self.pose = None
        self.end = time.time() + 0.05 + self.time


    def perform(self, connector, reevaluate=False):
        self.do_not_reevaluate()
        ipc = connector.get_ipc()
        if (not ipc.controlable) or ipc.get_state() == STATE_ANIMATION_RUNNING:
            # wait before doing something or popping till the robot is controlable
            return
        else:
            if self.started is True:
                if time.time() > self.end:
                    # we finished sucessfully
                    return self.pop()
            else:
                # start the kinematic task
                self.started = True
                self.pose = connector.get_pose()
                robot = connector.get_robot()
                task = connector.get_kinematic_task()
                robot.update(self.pose)
                task.perform(*self.args)
                robot.set_angles_to_pose(self.pose, self.time)  # todo this could block till its finished. ask robert
                if self.additional_angles is not None:
                    self.set_additional_angles()
                ipc.update(self.pose)
                return

    def set_additional_angles(self):
        for angle_tuple in self.additional_angles:
            self.pose.get_joint(angle_tuple[0]).goal = angle_tuple[1]