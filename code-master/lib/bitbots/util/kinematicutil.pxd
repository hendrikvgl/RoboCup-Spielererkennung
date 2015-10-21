from libcpp cimport bool
cimport numpy as np
from eigen cimport Vector2d, Vector3d, Matrix2d

from bitbots.util.pydatavector cimport PyDataVector
from bitbots.robot.kinematics cimport _Robot, Robot, JointID, int_to_JointID

cdef extern from "kinematic_util.hpp" namespace "Util::Kinematics::KinematicUtil":
    Vector2d get_robot_horizon (const _Robot& robot, unsigned char phase)
    Vector2d get_robot_horizon (const _Robot& robot, Vector3d& rpy)
    Vector3d get_camera_position(const _Robot& robot, unsigned char phase)
    void keep_robot_stable_ "Util::Kinematics::KinematicUtil::keep_robot_stable"(_Robot& robot, const Matrix2d& foot_size)
    void keep_robot_stable_ "Util::Kinematics::KinematicUtil::keep_robot_stable"(_Robot& robot, const Matrix2d& foot_size, int max_it)
    void keep_robot_stable_with_target_ "Util::Kinematics::KinematicUtil::keep_robot_stable_with_target"(_Robot& robot, const Matrix2d& foot_size, JointID endpoint, const Vector3d& target)
    void keep_robot_stable_with_target_ "Util::Kinematics::KinematicUtil::keep_robot_stable_with_target"(_Robot& robot, const Matrix2d& foot_size, JointID endpoint, const Vector3d& target, int max_it)

    void get_head_angles_for_distance_ "Util::Kinematics::KinematicUtil::get_head_angles_for_distance"(_Robot& robot, Vector2d pos, bool left_leg)
    void get_head_angles_for_distance_ "Util::Kinematics::KinematicUtil::get_head_angles_for_distance"(_Robot& robot, Vector2d pos, bool left_leg, double y_angle)
    void get_head_angles_for_distance_ "Util::Kinematics::KinematicUtil::get_head_angles_for_distance"(_Robot& robot, Vector2d pos, bool left_leg, double y_angle, double x_angle)
    Vector2d calculate_kinematic_robot_angle(_Robot& robot, int sup)


cpdef np.ndarray get_robot_horizon_p(Robot robot, int phase)
cpdef np.ndarray get_camera_position_p(Robot robot, int phase)
cpdef np.ndarray get_robot_horizon_p_deg(Robot robot, int phase)
cpdef np.ndarray get_robot_horizon_r(Robot robot, PyDataVector nrnpy)
cpdef keep_robot_stable(Robot robot, int max_it=?)
cpdef keep_robot_stable_with_target(Robot robot, int endpoint, np.ndarray target, int max_it=?)


cpdef get_head_angles_for_distance(Robot robot, np.ndarray pos, int left_leg)
cpdef get_head_angles_for_distance_with_y_offset(Robot robot, np.ndarray pos, int left_leg, float y_angle)
cpdef get_head_angles_for_distance_with_y_x_offset(Robot robot, np.ndarray pos, int left_leg, float y_angle, float x_angle)

cdef tuple kinematic_robot_angle(Robot robot, int phase)
