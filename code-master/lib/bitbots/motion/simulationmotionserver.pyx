# -*- coding: utf8 -*-
"""
SimulateMotionServer
^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 19.1.14: Aus dem motiopnserver rausgelöst (Nils Rokita)

Dieses Modul ermöglicht das Ausführen des Motionservers ohne anbindung zur
Hardware, es tut nur grundlegend so als wenn Motoren gesteuert werden würden.
"""
from bitbots.ipc.ipc cimport AbstractIPC
from bitbots.ipc import SharedMemoryIPC
from bitbots.robot.pypose cimport PyPose as Pose, PyJoint as Joint
from bitbots.util.pydatavector cimport PyDataVector as DataVector
from bitbots.util.pydatavector cimport PyIntDataVector as IntDataVector

from cpython.exc cimport PyErr_CheckSignals

import math
import time
import json
import traceback

from bitbots.debug.debug cimport Scope
cdef Scope debug = Scope("Motion.Server")

cdef sign(x):
    return -1 if x < 0 else 1

cdef class SimulationMotionServer(BaseMotionServer):
    """
    Mit dieser Klasse können die Gelenke des Roboters etwas
    simuliert werden. Ein SimulationMotionServer kann am einfachsten
    über die Methode :func:`simulate` gestartet werden.
    """
    def __init__(self, ipc):
        super(SimulationMotionServer, self).__init__(ipc, False, True, False, False)
        self.next_pose = self.ipc.get_pose()

    cpdef update_sensor_data(self):
        self.robo_pose = self.next_pose
        self.robo_gyro = IntDataVector(0, 0, 0)
        self.robo_accel = IntDataVector(0, 0, 0)
        self.raw_gyro= IntDataVector(0, 0, 0)
        time.sleep(0.003)

    cpdef apply_goal_pose(self):
        cdef bytes name
        cdef Joint joint, next
        cdef dt = 0.008

        cdef Pose pose = self.goal_pose
        if pose is None:
            return

        time.sleep(dt - 0.002)
        for name, joint in pose.joints:
            next = self.next_pose[name]
            if abs(next.position - joint.goal) < 2:
                next.position = joint.goal
            else:
                r = sign(next.position - joint.goal)
                speed = joint.speed if joint.speed > 0 else 702.42
                pos = joint.goal - speed * dt * r
                if r != sign(pos - joint.goal):
                    next.position = joint.goal
                else:
                    next.position = pos


cpdef simulate(ipc=None):
    """ Siehe :class:`SimulationMotionServer`.  Dies ist die Bootsrap
    methode für dien SimulateMotionServer"""
    debug << "Start Simulate Motionseerver"
    ipc = ipc or SharedMemoryIPC(client=False)
    ms = SimulationMotionServer(ipc)
    run(ms)
