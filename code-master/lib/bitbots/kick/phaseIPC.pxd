# -*- coding: utf-8 -*-
from libcpp cimport bool
cimport numpy as np
np.import_array()
import time
from bitbots.robot.pypose cimport PyPose as Pose
from bitbots.robot.kinematics cimport Robot
from bitbots.kick.functionWrapper cimport SingleArgFunctionWrapper, DoubleArgFunctionWrapper, ValidateFunctionWrapper
from bitbots.kick.bezier cimport Bezier

cdef inline float degrees(float radians):
    return radians * 180 / 3.1415926535897932384626433832795028841971693

cdef inline float radians(float degrees):
    return degrees / 180 * 3.1415926535897932384626433832795028841971693

cdef class Phase(object):
    cdef float delta
    cdef float epsilon
    cdef Robot robot
    cdef DoubleArgFunctionWrapper distance
    cdef SingleArgFunctionWrapper cog
    cdef SingleArgFunctionWrapper cog_distance
    cdef ValidateFunctionWrapper validate
    cdef int max_iter
    cdef list iter
    cdef np.ndarray direction
    cdef Bezier bezier
    cdef bool no_cog

    cdef np.ndarray get_direction(self)
    cdef Bezier get_bezier(self)
    cdef list get_iter(self)
    cdef Pose calc_angles(self, Pose ipc_pose,float t)
    cdef np.ndarray step(self, np.ndarray  angles, np.ndarray dest, float error)

cdef np.ndarray normalize_vector(np.ndarray correction, float error, float weight=?)
cdef np.ndarray pose_to_array(Pose ipc_pose)
cdef Pose array_to_pose(np.ndarray array)

cdef class Phaseholer(object):
    cdef int num, idx
    cdef Phase phase
    cdef Phaseholer next

    cdef Phase get(self, int idx)
    cdef append(self, Phase phase)
    cdef remove_first(self)
    cdef int get_num(self)
