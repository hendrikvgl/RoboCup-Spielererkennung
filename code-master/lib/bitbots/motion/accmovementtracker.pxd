#-*- coding:utf-8 -*-
__author__ = 'Sören Nykamp'

import time
from bitbots.util.pydatavector cimport PyDataVector

cdef extern from "cmath":
    double sin(double)
    double cos(double)
    double sqrt(double)

cdef class AccMovementTracker(object):
    cdef PyDataVector movement, movement_last_period, velo
    cdef object start_this_period, start_last_period, last_asked, last_input

    cdef clear_to_zero(self)
    cdef get_actual_vector(self)
    cdef apply_acceleration(self, float x, float y, float z, object input_time)
