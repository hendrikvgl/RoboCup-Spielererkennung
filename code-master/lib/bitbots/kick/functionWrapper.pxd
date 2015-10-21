from libcpp cimport bool
from bitbots.robot.kinematics cimport Robot
cimport numpy as np

cdef class ValidateFunctionWrapper(object):
    cdef bool (*val_func)(Robot)

    cdef set(self, bool (*val_func)(Robot))
    cdef bool apply(self, Robot robot)

cdef class SingleArgFunctionWrapper(object):
    cdef float (*cog_func)(Robot)

    cdef set(self, float (*cog_func)(Robot))
    cdef float apply(self, Robot robot)

cdef class DoubleArgFunctionWrapper(object):
    cdef float (*dist_func)(Robot, np.ndarray)

    cdef set(self, float (*cog_func)(Robot, np.ndarray arr))
    cdef float apply(self, Robot robot, np.ndarray arr)
