#ifndef _IMAGE_POINT_TO_LOCATION_TRANSFORMER_HPP
#define _IMAGE_POINT_TO_LOCATION_TRANSFORMER_HPP

#include "../robot/pose.hpp"
#include "../robot/kinematic_robot.hpp"
#include "../debug/debug.hpp"

#include <Eigen/Core>
#include <Eigen/Householder>
#include <Eigen/QR>

#include <vector>
#include "../debug/debugmacro.h"

namespace Location{

static const Eigen::Vector4f ORIGIN(0, 0, 0, 1);
static const Eigen::Vector4f X_AXIS(1, 0, 0, 0);
static const Eigen::Vector4f Y_AXIS(0, 1, 0, 0);
static const Eigen::Vector4f Z_AXIS(0, 0, 1, 0);

class Image_Point_To_Location_Transformer
{
private:

Robot::Kinematics::KRobot robot;

Eigen::Matrix4f to_floor;
Eigen::Vector4f head;
float m_camera_angle_factor;
Eigen::Matrix3f A;

mutable Debug::Scope m_debug;

    /**
     * Sets some parameters for efficient point transformation
     * Returns wheater the Robot definetly stands on one leg
     */
    int set_floor_matrix_and_head();

public:
EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    Image_Point_To_Location_Transformer(const Robot::Kinematics::KRobot& robot)
    :robot(robot), to_floor(Eigen::Matrix4f::Identity()), head(0,0,0,0)
    , m_camera_angle_factor(1), m_debug("Locator")
    {//camera_angle_factor 1.07 oder 1.0471
        A.col(1) << 1, 0, 0;
        A.col(2) << 0, 1, 0;
    }

    double get_ray_motor_distance(const Eigen::Vector2d& image_point);

    const Robot::Kinematics::KRobot& get_robot() const {
        return robot;
    }

    float get_camera_angle() const
    {
        return m_camera_angle_factor;
    }
    const Eigen::Vector4f& get_head() const
    {
        return head;
    }
    const Eigen::Matrix4f& get_to_floor() const
    {
        return to_floor;
    }
    Eigen::Matrix3f get_A() const
    {
        return A;
    }

    void set_camera_angle(float deg) {
        m_camera_angle_factor = 2 * tan(deg * degree_to_rad * 0.5);
    }

    /**
        Setzt die aktuelle Stellung der Gelenke des Roboters.
    */
    int update_pose(const Robot::Pose& pose) {
        robot.update(pose);
        return set_floor_matrix_and_head();
    }

    /**
     * Transforms a given imagepoint so that the result represents the position
     * of the requested object in an coordinate system relative to the robot
     */
    inline
    Eigen::Vector2f transform_point(const Eigen::Vector2f& normalized_image_point);

    /**
     * z_offset in mm, nicht in m oder cm oder so....
     */
    Eigen::Vector2f transform_point_with_offset(const Eigen::Vector2f& normalized_image_point, float z_offset);

    std::vector<bool> convex_hull(const Eigen::Matrix2Xf& image_points);

private:
    /**
     * The real transformation of an image point to a position in a coordinate
     * System with the robot as origin
     */
    inline
    Eigen::Vector2f transform(const Eigen::Vector2f& normalized_image_point
        , const Eigen::Vector4f& head);

    inline Eigen::Vector2f transform(const Eigen::Vector2f& image_point, const Eigen::Vector4f& head, const Eigen::Matrix4f& to_floor);
};



inline Eigen::Vector2f Image_Point_To_Location_Transformer::transform_point(
    const Eigen::Vector2f& image_point)
{
    Eigen::Vector2f result = transform(image_point, head);

    return result;
}

inline Eigen::Vector2f Image_Point_To_Location_Transformer::transform(
    const Eigen::Vector2f& image_point, const Eigen::Vector4f& head)
{
    //The ray of for the point: When going forward one unit on x-axis, then the points x-position on y and the points y-position on z-axis
    Eigen::Vector4f ray(1, image_point.x() * m_camera_angle_factor, image_point.y() * m_camera_angle_factor, 0);
    A.col(0) = -(to_floor * ray).head<3>();

    // Nach u und v auflösen
    Eigen::Vector3f tuv = A.householderQr().solve(head.head<3>());
    float u = tuv(1), v = tuv(2);
    //DEBUG(3,"HeadHeight", head(1));
    return Eigen::Vector2f(u, v);
}

inline Eigen::Vector2f Image_Point_To_Location_Transformer::transform(
    const Eigen::Vector2f& image_point, const Eigen::Vector4f& head, const Eigen::Matrix4f& floor)
{
    //The ray of for the point: When going forward one unit on x-axis, then the points x-position on y and the points y-position on z-axis
    Eigen::Vector4f ray(1, image_point.x() * m_camera_angle_factor, image_point.y() * m_camera_angle_factor, 0);
    A.col(0) = -(floor * ray).head<3>();

    // Nach u und v auflösen
    Eigen::Vector3f tuv = A.householderQr().solve(head.head<3>());
    float u = tuv(1), v = tuv(2);
    //DEBUG(3,"HeadHeight", head(1));
    return Eigen::Vector2f(u, v);
}


//namespace
}
#endif
