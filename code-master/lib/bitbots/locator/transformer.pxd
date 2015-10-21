cimport numpy as np
from libcpp.vector cimport vector
from libcpp cimport bool
from eigen cimport *
from bitbots.robot.pose cimport Pose
from bitbots.robot.pypose cimport PyPose
from bitbots.robot.kinematics cimport Robot, _Robot

cdef extern from "image_point_to_location_transformer.hpp":
    cdef cppclass _Transformer "Location::Image_Point_To_Location_Transformer":
        _Transformer(const _Robot& robot)
        int update_pose(Pose& pose)
        _Robot& get_robot()
        void set_camera_angle(float deg)
        float get_camera_angle()
        Vector2f transform_point_with_offset(Vector2f image_point, float z_offset)
        double get_ray_motor_distance(Vector2d image_point)
        vector[bool] convex_hull(const MatrixXf& image_points)

    _Robot* deconstify_robot "const_cast< ::Robot::Kinematics::KRobot*>" (const _Robot*)

cdef class Transformer:
    cdef _Transformer* transformer

    cpdef update_pose(self, PyPose pose)
    cpdef set_camera_angle(self, float deg)
    cpdef transform_point_to_location(self, float x_point_in_picture, \
            float y_point_in_picture, float z_offset)
    cpdef transform_points(self, np.ndarray points, float offset=?)
    cpdef debugprint(self)
    cpdef get_camera_angle(self)
    cpdef float ray_motor_distance(self, object point)
    cpdef list convex_hull(self, object image_points)
