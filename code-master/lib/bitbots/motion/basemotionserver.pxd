# -*- coding: utf8 -*-
from libcpp cimport bool
from bitbots.ipc.ipc cimport AbstractIPC

from bitbots.robot.pypose cimport PyPose as Pose, PyJoint as Joint
from bitbots.util.pydatavector cimport PyDataVector as DataVector
from bitbots.util.pydatavector cimport PyIntDataVector as IntDataVector
from bitbots.lowlevel.controller.controller cimport Controller, BulkReadPacket, SyncWritePacket
from bitbots.util.kalman cimport TripleKalman
from bitbots.motion.animation cimport Animation

include "zmpwalking.pxi"
include "accmovementtracker.pxi"

#auch in ipc/ipc.pyx anpassen
cdef public enum:
    STATE_CONTROLABLE = 1
    STATE_FALLING
    STATE_FALLEN
    STATE_GETTING_UP
    STATE_ANIMATION_RUNNING
    STATE_BUSY
    STATE_STARTUP
    STATE_PENALTY
    STATE_PENALTY_ANIMANTION
    STATE_RECORD
    STATE_SOFT_OFF
    STATE_WALKING

cdef public enum:
    FALLEN_BOTTOM_UP = 1
    FALLEN_FRONT_UP
    FALLEN_BEND_FORWARD
    FALLEN_SQUATTED
    FALLEN_UPRIGHT

cdef state_to_string(int state)

cdef class BaseMotionServer(object):
    cdef readonly AbstractIPC ipc
    cdef public Pose robo_pose
    cdef public IntDataVector robo_accel, raw_gyro
    cdef public DataVector kin_robo_angle, robo_angle
    cdef double smooth_robo_angle_x
    cdef double long_time_robo_angle_x
    cdef public IntDataVector robo_gyro
    cdef public int button1, button2
    cdef readonly Pose goal_pose
    cdef readonly int last_version
    cdef readonly led_head, led_eye
    cdef int state
    cdef int fallState
    cdef bool with_gyro
    # post_anim_state ist object weil es sonst kein None gibt
    cdef object post_anim_state
    cdef Animation next_animation
    cdef object animfunc
    cdef object startup_time
    cdef object last_client_update
    cdef int data_send_last  # zum reduzieren der debugdaten
    cdef int dieflag
    cdef int standupflag
    cdef int softoff
    cdef object config
    cdef object nice
    cdef int softstart
    cdef DataVector smooth_accel, smooth_gyro, not_much_smoothed_gyro
    cdef bool falling_activated
    cdef float falling_ground_coefficient
    cdef object falling_motor_degrees_front, falling_motor_degrees_back, falling_motor_degrees_left, falling_motor_degrees_right
    cdef float falling_threshold_front, falling_threshold_back, falling_threshold_left, falling_threshold_right
    cdef TripleKalman gyro_kalman, kinematic_kalman

    cdef ZMPWalkingEngine walking
    cdef int zmp_foot_phase
    cdef int walk_forward
    cdef int walk_sideward
    cdef int walk_angular
    cdef int walk_active
    cdef object walkready_animation
    cdef bool dynamic_animation
    cdef bool with_tiltX
    cdef bool robo_angle_stop
    cdef bool smooth_robo_angle_stop_value
    cdef double smooth_robo_angle_smoothing
    cdef double walking_started


    cdef set_state(self, int state)
    cpdef update_forever(self)
    cpdef animate(self, name, post_anim_state=?, dict animation=?)
    cpdef update_once(self)
    cpdef update_sensor_data(self)
    cpdef apply_goal_pose(self)
    cpdef switch_motor_power(self, state)
    cpdef evaluate_state(self)
    cpdef check_queued_animations(self)
    cdef info(self, text)
    cpdef check_fallen(self)
    cpdef check_fallen_forwardAndBackward(self)
    cpdef check_fallen_sideways(self)
    cpdef update_goal_pose(self)
    cpdef walkready_pose(self, duration=?)
    cpdef load_falling_data(self)
    cpdef set_falling_pose(self, object falling_motor_degrees)

    cdef init_walking(self)
    cdef ZMPWalkingEngine create_and_parametrize_walking_engine(self)
    cdef Pose calculate_walking(dself)
    cdef void walking_start(self)
    cdef void walking_reset(self)
    cdef void walking_stop(self)

cdef run(BaseMotionServer ms)
