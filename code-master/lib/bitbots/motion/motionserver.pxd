# -*- coding: utf8 -*-

from eigen cimport *

from bitbots.lowlevel.controller.controller cimport Controller, BulkReadPacket
from bitbots.util.datavector cimport IntDataVector as CIntDataVector
from bitbots.util.datavector cimport DataVector as CDataVector
from bitbots.util.pydatavector cimport PyDataVector as DataVector
from bitbots.util.pydatavector cimport PyIntDataVector as IntDataVector
from bitbots.motion.basemotionserver cimport BaseMotionServer, run, STATE_PENALTY, STATE_SOFT_OFF, STATE_WALKING
from bitbots.motion.basemotionserver cimport STATE_GETTING_UP, STATE_RECORD, STATE_ANIMATION_RUNNING
from bitbots.robot.kinematics cimport Robot
from libcpp cimport bool
cdef class MotionServer(BaseMotionServer):
    cdef Controller ctrl
    cdef BulkReadPacket read_packet
    cdef BulkReadPacket read_packet2
    cdef BulkReadPacket read_packet3
    cdef last_io_success
    cdef list motors
    cdef int is_soft_off
    cdef int dxl_power
    cdef bool cm_370
    cdef dict motor_ram_config
    cdef dict last_overload
    cdef dict overload_count
    cdef object joint_offsets # kein dict da helperdict...
    cdef object joint_manager
    cdef double last_gyro_update_time
    cdef Robot robot
    cdef tuple last_kinematic_robot_angle

    cdef set_motor_ram(self)
    cdef init_read_packet(self)
    cpdef update_sensor_data(self)
    cpdef apply_goal_pose(self)
    cpdef switch_motor_power(self, state)

cpdef bootstrap(device=?, ipc=?, dieflag=?, standupflag=?,
    softoff=?, softstart=?, starttest=?, cm_370=?)

cdef extern from "cmath" namespace "std":
    double asin(double)
    double acos(double)

cdef extern from "zmp_math_basics.h":
    double rad_to_degree, degree_to_rad

cdef inline double calc_sin_angle(const Vector3d& fst, const Vector3d& sec):
    if(fst.norm() == 0 or sec.norm() == 0):
        return 0 #TODO Rückgabewert sinvoll?
    return asin(fst.dot(sec) / (fst.norm() * sec.norm())) * rad_to_degree

cdef inline double calc_cos_angle(const Vector3d& fst, const Vector3d& sec):
    return acos(fst.dot(sec) / (fst.norm() * sec.norm())) * rad_to_degree

cdef inline CDataVector calculate_robot_angles(const CIntDataVector& rawData):
    cdef Vector3d raw = Vector3d(rawData.get_x(), rawData.get_y(), rawData.get_z())
    cdef double roll_angle, pitch_angle, yaw_angle

    pitch_angle = calc_sin_angle(raw, unitY3d())
    if(raw.z() < 0 and raw.y() < 0):
        pitch_angle = - pitch_angle - 180
    elif(raw.z() < 0 and raw.y() > 0):
        pitch_angle = 180 - pitch_angle

    roll_angle = calc_sin_angle(raw, unitX3d())

    #TODO mir ist noch keiner schlaue Formel für diesen Wingkel eingefallen
    yaw_angle = 0

    #print "pitch %f, roll %f" % (pitch_angle, roll_angle)

    return CDataVector(-roll_angle, -pitch_angle, yaw_angle)

from bitbots.util.config import get_config

cdef inline IntDataVector verdrehe_bla(IntDataVector vec):
    c = get_config()
    cdef int x_angle = c["X"]
    cdef int y_angle = c["Y"]
    cdef Vector3d v = Vector3d(vec.x, vec.y,vec.z)
    cdef Vector3d result
    result = AngleAxisd(x_angle * degree_to_rad, Vector3d(1,0,0)) * (AngleAxisd(y_angle * degree_to_rad, Vector3d(0,1,0))* v)
    #result =  * result
    return IntDataVector(result.x(), result.y(), result.z())
