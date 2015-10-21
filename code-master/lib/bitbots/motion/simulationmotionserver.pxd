# -*- coding: utf8 -*-

from bitbots.robot.pypose cimport PyPose as Pose


from bitbots.motion.basemotionserver cimport BaseMotionServer, run


cdef class SimulationMotionServer(BaseMotionServer):
    cdef Pose next_pose

    cpdef update_sensor_data(self)
    cpdef apply_goal_pose(self)

cpdef simulate(ipc=?)
