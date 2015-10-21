# -*- coding: utf-8 -*-
from libcpp cimport bool
cimport numpy as np
np.import_array()


cdef class Bezier(object):
    cdef np.ndarray p0
    cdef np.ndarray p1
    cdef np.ndarray p2
    cdef np.ndarray p3
    cdef int dim

    cdef float posAxis(self, float t, int axis)
    cdef list pos(self, float t)
    cpdef visualize(self, int res, bool only_data=?, int phase=?)
