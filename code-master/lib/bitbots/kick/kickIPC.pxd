# -*- coding: utf-8 -*-
from libcpp cimport bool
cimport numpy as np
np.import_array()

from bitbots.ipc.ipc cimport SharedMemoryIPC
from bitbots.robot.pypose cimport PyPose as Pose
from bitbots.robot.kinematics cimport Robot
from bitbots.kick.functionWrapper cimport SingleArgFunctionWrapper, DoubleArgFunctionWrapper, ValidateFunctionWrapper
cimport bitbots.kick.vector as v
from bitbots.kick.bezier cimport Bezier
from bitbots.kick.phaseIPC cimport Phase, Phaseholer
from bitbots.kick.functionWrapper cimport SingleArgFunctionWrapper, DoubleArgFunctionWrapper

cdef inline float radians(float degrees):
    return degrees / 180 * 3.1415926535897932384626433832795028841971693

cdef class Kinematic(object):
    cdef SharedMemoryIPC ipc
    cdef Robot robot
    #cdef list phases
    cdef Phaseholer phases
    cdef np.ndarray prev_dir
    cdef int phasenum
    cdef int frame

    cdef kick(self, np.ndarray ball_pos, float kick_angle, bool rightfoot=?)
    cdef add_phase(self, DoubleArgFunctionWrapper dist_func, SingleArgFunctionWrapper mass_func, \
                    SingleArgFunctionWrapper mass_dist_func, ValidateFunctionWrapper val_func, \
                    np.ndarray start, np.ndarray target, np.ndarray direction=?)
    cdef execute(self)
    cdef executePhase(self, Phase phase, float t_total=?, float delta=?)
    cdef update_pose(self, Pose cur_pose, Pose new_pose, float delta)

cdef float kick_r_foot_cog(Robot robot)
cdef float kick_r_foot_cog_distance(Robot robot)
cdef float kick_r_foot_distance(Robot robot, np.ndarray dest)
cdef bool kick_r_foot_validate(Robot robot)
cdef float kick_l_foot_cog(Robot robot)
cdef float kick_l_foot_cog_distance(Robot robot)
cdef float kick_l_foot_distance(Robot robot, np.ndarray dest)
cdef bool kick_l_foot_validate(Robot robot)

cdef plot(Robot robot, np.ndarray ball_pos=?, bool png=?, int frame=?, Bezier bezier=?, \
            np.ndarray mass=?, bool gplot=?)

