# -*- coding: utf-8 -*-
cimport numpy as np

cdef np.ndarray orig()
cdef np.ndarray eye()
cdef np.ndarray roll(float angle)
cdef np.ndarray pitch(float angle)
cdef np.ndarray yaw(float angle)
cdef np.ndarray rot(float angle)
cdef np.ndarray rot3d(float angle, int axis)
cdef np.ndarray trans(float l)
cdef np.ndarray trans3d(float z=?,float  y=?, float x=?)
cdef np.ndarray position(list joints)
cdef float distance(np.ndarray p1,np.ndarray p2)
cdef np.ndarray homogen(np.ndarray v)
