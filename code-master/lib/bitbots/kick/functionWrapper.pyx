from libcpp cimport bool
from bitbots.robot.kinematics cimport Robot
import numpy as np
cimport numpy as np
np.import_array()

cdef class ValidateFunctionWrapper(object):
    def __cinit__(self):
        pass

    cdef set(self, bool (*val_func)(Robot)):
        self.val_func = val_func

    cdef bool apply(self, Robot robot):
        return self.val_func(robot)

    #def __call__(self, Robot robot):
    #    return apply.val_func(robot)

cdef class SingleArgFunctionWrapper(object):
    def __cinit__(self):
        pass

    cdef set(self, float (*cog_func)(Robot)):
        self.cog_func = cog_func

    cdef float apply(self, Robot robot):
        return self.cog_func(robot)

    #def __call__(self, Robot robot):
    #    return self.apply(robot)

cdef class DoubleArgFunctionWrapper(object):
    def __cinit__(self):
        pass

    cdef set(self, float (*dist_func)(Robot, np.ndarray)):
        self.dist_func = dist_func

    cdef float apply(self, Robot robot, np.ndarray arr):
        return self.dist_func(robot, arr)

    #def __call__(self, Robot robot, np.ndarray arr):
    #    return self.apply(robot, arr)
