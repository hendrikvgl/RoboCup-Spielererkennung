# -*- coding: utf8 -*-

from bitbots.ipc.ipcprovider cimport IPCProvider
from bitbots.robot.pypose cimport PyPose as Pose
from bitbots.util.pydatavector cimport PyDataVector as DataVector
from bitbots.util.pydatavector cimport PyIntDataVector as IntDataVector

import numpy as np
cimport numpy as np
np.import_array()

from libcpp cimport bool

cdef class AbstractIPC:
    cdef IPCProvider *ipc
    cdef readonly force
    cdef readonly record

    cpdef int get_version(self)

    cpdef Pose get_pose(self)
    cpdef Pose get_pose_ref(self)

    cpdef update(self, Pose pose)
    cpdef update_positions(self, Pose pose)

    cpdef IntDataVector get_gyro(self)
    cpdef set_gyro(self, IntDataVector dv)

    cpdef DataVector get_robot_angle(self)
    cpdef set_robot_angle(self, DataVector dv)

    cpdef IntDataVector get_accel(self)
    cpdef set_accel(self, IntDataVector dv)

    cpdef DataVector get_eye_color(self)
    cpdef set_eye_color(self, DataVector dv)

    cpdef DataVector get_forehead_color(self)
    cpdef set_forehead_color(self, DataVector dv)

    cpdef set_state(self, int state)
    cpdef int get_state(self)

    cpdef set_button1(self, bool state)
    cpdef bool get_button1(self)

    cpdef set_button2(self, bool state)
    cpdef bool get_button2(self)

    cpdef set_motion_state(self, int state)
    cpdef int get_motion_state(self)

    cpdef set_walking_forward(self, int speed)
    cpdef int get_walking_forward(self)

    cpdef set_walking_sidewards(self, int speed)
    cpdef int get_walking_sidewards(self)

    cpdef set_walking_angular(self, int speed)
    cpdef int get_walking_angular(self)

    cpdef set_walking_activ(self, bool state)
    cpdef bool get_walking_activ(self)

    cpdef set_walking_foot_phase(self, unsigned char state)
    cpdef int get_walking_foot_phase(self)

    cpdef reset_tracking(self)
    cpdef bool get_reset_tracking(self)

    cpdef DataVector get_last_track(self)
    cpdef set_last_track(self, DataVector track)

    cpdef DataVector get_track(self)
    cpdef set_track(self, DataVector track)

    cpdef int get_last_track_time(self)
    cpdef set_last_track_time(self, int time)

    cpdef set_image(self, int width, int height, np.ndarray image)
    cpdef np.ndarray get_image(self)
    cpdef int get_image_width(self)
    cpdef int get_image_height(self)

cdef class SharedMemoryIPC(AbstractIPC):
    pass

