#include <assert.h>
#include <iostream>
#include <Eigen/Core>
#include <Eigen/Geometry>

#include "kinematic_util.hpp"
#include "math_constants.h"
#include "../robot/jointids.hpp"
#include "../robot/kinematic_task.hpp"
#include "../motion/zmp_math_basics.h"
#include "../debug/debugmacro.h"

using namespace Util;
using namespace Kinematics;
using namespace Eigen;
namespace Kin = Robot::Kinematics;

using ::Robot::Kinematics::ChainIds;
using std::cout;
using std::endl;

Vector2d KinematicUtil::get_robot_horizon(const KRobot& robot, uint8_t phase)
{
    //Determine support foot
    Affine3d support_foot;
    if(phase == SupportLeg::left) {
        support_foot = robot.get_joint_by_id(Kin::JointIds::LFootEndpoint).get_chain_matrix_inverse();
    } else {
        support_foot = robot.get_joint_by_id(Kin::JointIds::RFootEndpoint).get_chain_matrix_inverse();
    }
    // Calculating the cameras global endpoint
    Matrix4d camera_endpoint = (support_foot * robot.get_joint_by_id(Kin::JointIds::Camera).get_chain_matrix()).matrix();

    // Calculating the camera's tilt angle. This will be used to place a horizon line in the camera image
    // Simple vector plain angle calculation is used, but both vectors, are normalized, so we don't need to divide the result
    Vector3d camera_tilt = (camera_endpoint * Vector4d::UnitX()).head<3>();
    double camera_angle = asin(camera_tilt.dot(Vector3d::UnitZ()));

    Vector3d camera_pan = (camera_endpoint * Vector4d::UnitY()).head<3>();
    double camera_rotation = asin(camera_pan.dot(Vector3d::UnitZ()));

    return Vector2d(camera_angle, camera_rotation);
}

Eigen::Vector3d KinematicUtil::get_camera_position(const KRobot& robot, uint8_t phase)
{
    Affine3d support_foot;
    if(phase == SupportLeg::left) {
        support_foot = robot.get_joint_by_id(Kin::JointIds::LFootEndpoint).get_chain_matrix_inverse();
    } else {
        support_foot = robot.get_joint_by_id(Kin::JointIds::RFootEndpoint).get_chain_matrix_inverse();
    }
    // Calculating the cameras global endpoint
    Matrix4d camera_endpoint = (support_foot * robot.get_joint_by_id(Kin::JointIds::Camera).get_chain_matrix()).matrix();

    return camera_endpoint.col(3).head<3>();
}

Eigen::Vector2d KinematicUtil::get_robot_horizon(KRobot& robot, const Eigen::Vector3d& rpy)
{
    robot.set_initial_angles(rpy, Robot::Kinematics::ChainIds::HeadChain);
    // Calculating the cameras global endpoint
    Matrix4d camera_endpoint = robot.get_joint_by_id(Kin::JointIds::Camera).get_chain_matrix().matrix();
    robot.reset_initial_angles();

    // Calculating the camera's tilt angle. This will be used to place a horizon line in the camera image
    // Simple vector plain angle calculation is used, but both vectors, are normalized, so we don't need to divide the result
    Vector3d camera_tilt = (camera_endpoint * Vector4d::UnitX()).head<3>();
    double camera_angle = asin(camera_tilt.dot(Vector3d::UnitZ()));

    Vector3d camera_pan = (camera_endpoint * Vector4d::UnitY()).head<3>();
    double camera_rotation = asin(camera_pan.dot(Vector3d::UnitZ()));

    return Vector2d(camera_angle, camera_rotation);
}


Eigen::Vector2d KinematicUtil::calculate_kinematic_robot_angle(const KRobot& robot, int sup) {
    JointIds supId = (sup == SupportLeg::left? JointIds::LFootEndpoint: JointIds::RFootEndpoint);
    Eigen::Affine3d suppport_transform = robot[supId].get_chain_matrix_inverse();
    Eigen::Vector3d angle = suppport_transform.linear().col(2);//.normalized();
    if(angle == Eigen::Vector3d::UnitZ()) {
        return Eigen::Vector2d::Zero();
    }
    //TODO I think I still need some normalisation here, but for now this should be sufficient. I only expect a rotation on one axis,
    // so the normalization should not be crucial required.
    double x_part = Vector2d{angle.y(), angle.z()}.normalized().x();
    double y_part = Vector2d{angle.x(), angle.z()}.normalized().x();
    // I don't know how to fix the scaling for the second angle on the x-axis, but it's not so important, I'll leave this as TODO
    // TODO fix the scaling, so that we can handle both axes correctly and simultaneously
    return angle.z() < 0.0 ? Eigen::Vector2d{-asin(x_part), pi - asin(y_part)}
                         : Eigen::Vector2d{-asin(x_part), asin(y_part)};
}

SupportLeg KinematicUtil::determine_support_leg(const KRobot& robot, const double threshold) {
    const Affine3d& l_foot = robot.get_joint_by_id(Kin::JointIds::LFootEndpoint).get_chain_matrix();
    Affine3d l_foot_inv = robot.get_joint_by_id(Kin::JointIds::LFootEndpoint).get_chain_matrix_inverse();
    const Affine3d& r_foot = robot.get_joint_by_id(Kin::JointIds::RFootEndpoint).get_chain_matrix();
    Affine3d r_foot_inv = robot.get_joint_by_id(Kin::JointIds::RFootEndpoint).get_chain_matrix_inverse();
    double left_based_height = (l_foot_inv * r_foot).translation()(2);
    double right_based_height = (r_foot_inv * l_foot).translation()(2);
    if(left_based_height > 0 && right_based_height < 0)
        return SupportLeg::left;
    if(left_based_height < 0 && right_based_height > 0)
        return SupportLeg::right;
    else if(fabs(left_based_height) < threshold && fabs(right_based_height) < threshold)
        return SupportLeg::both;
    L_DEBUG(std::cerr<<"Unknown support Foot"<<std::endl);
    return SupportLeg::unknown;
}

void KinematicUtil::keep_robot_stable(KRobot& robot, const Matrix2d& foot_size, double security_offset, int max_it) {
    assert(security_offset > 0);
    SupportLeg sup = determine_support_leg(robot);
    Kin::JointIds foot_id = sup == left? Kin::JointIds::LFootEndpoint : Kin::JointIds::RFootEndpoint;
    Kin::ChainIds chain_id = sup == left? Kin::ChainIds::LLegChain : Kin::ChainIds::RLegChain;
    Matrix4d sup_foot_inv = robot.get_joint_by_id(foot_id).get_chain_matrix_inverse().matrix();
    Vector4d cog = robot.get_centre_of_gravity();
    cog = (Vector4d() << (sup_foot_inv * (Vector4d()<<cog.head<3>(), 1).finished()).head<3>(), cog(3)).finished();

    double cog_is_in_front = cog.x() + security_offset - foot_size(0,0);
    double cog_is_behind = -cog.x() + security_offset + foot_size(1,0);

    double cog_is_left;
    double cog_is_right;
    if(sup == left) {
        cog_is_left = cog.y() + security_offset - foot_size(0,1);
        cog_is_right = -cog.y() + security_offset + foot_size(1,1);
    } else {
        cog_is_left = cog.y() + security_offset + foot_size(1,1);
        cog_is_right = -cog.y() + security_offset - foot_size(0,1);
    }

    if(sup == unknown && cog_is_left > 0) {
        cog_is_left = 0;
    }

    Vector4d cog_target_offset(0, 0, 0, 1);
    assert(!(cog_is_behind > 0 && cog_is_in_front > 0));
    assert(!(cog_is_right > 0 && cog_is_left > 0));

    if(cog_is_behind > 0)
        cog_target_offset.x() = cog_is_behind;
    if(cog_is_in_front > 0)
        cog_target_offset.x() = -cog_is_in_front;
    if(cog_is_left > 0)
        cog_target_offset.y() = cog_is_left;
    if(cog_is_right > 0)
        cog_target_offset.y() = -cog_is_right;
    L_DEBUG(std::cout<<"FootSize\n"<<foot_size<<std::endl);
    L_DEBUG(std::cout<<"Front: "<< cog_is_in_front<<" Behing: "<<cog_is_behind<<" Left: "<<cog_is_left<<" Right: "<<cog_is_right<<std::endl);
    L_DEBUG(std::cout<<"Cog:  "<<cog.head<3>().transpose()<<" Proposed offset: "<<cog_target_offset.head<3>().transpose()<<std::endl);
    if(cog_target_offset.head<2>() == Vector2d::Zero())
        return;

    Vector4d cog_target = cog - cog_target_offset;
    L_DEBUG(std::cout<<"CogTarget:  "<<cog_target.head<3>().transpose()<<std::endl);

    Kin::KinematicTask task(robot);
    task.perform_centre_of_gravity_task(chain_id, cog_target.head<3>(), std::set<int>(), 1e0, max_it, Kin::KinematicTask::DisableType::direct_chain);
}

void KinematicUtil::keep_robot_stable_with_target(KRobot& robot, const Matrix2d& foot_size, Robot::Kinematics::JointIds endpoint, const Eigen::Vector3d& target, double security_offset, int max_it) {
    Kin::KinematicTask task(robot);
    SupportLeg sup = determine_support_leg(robot);
    Kin::JointIds foot_id = sup == left? Kin::JointIds::LFootEndpoint : Kin::JointIds::RFootEndpoint;
    task.perform_task(foot_id, endpoint, target, Kin::KJoint::AxisType::Position);
    keep_robot_stable(robot, foot_size, security_offset, max_it);
}

template<int additional_parameter>
inline void KinematicUtil::get_head_angles_for_distance_intern(KRobot& robot, const Vector2d& pos, bool left_leg, double y_angle, double x_angle) {
    Affine3d base, inv_base;
    //handle support leg
    if(left_leg) {
        inv_base = robot.get_joint_by_id(JointIds::LFootEndpoint).get_chain_matrix_inverse();
        base = robot.get_joint_by_id(JointIds::LFootEndpoint).get_chain_matrix();
    } else {
        inv_base = robot.get_joint_by_id(JointIds::RFootEndpoint).get_chain_matrix_inverse();
        base = robot.get_joint_by_id(JointIds::RFootEndpoint).get_chain_matrix();
    }
    Vector3d head_pos = (inv_base.matrix() * robot.get_joint_by_id(JointIds::Camera).get_endpoint()).head<3>();
    head_pos.y() = 0;
    //difference vector between head and the point to focus
    Vector3d diff = (Vector3d()<<pos, 0).finished() - head_pos;
    Vector3d target = base.linear() * diff.normalized();
    //handle "special" tasks. Those tasks where another point than the middle point should have the given distance.
    if(additional_parameter > 0) {
        Vector3d y_orthogonal, x_orthogonal;
        //Calculate an orthogonal vector to have a rotation axis when rotating the target vector, so that y-angle has the given distance
        y_orthogonal = diff.cross(Vector3d::UnitZ()).normalized();
        L_DEBUG(cout<<"Orthogonale:\n"<<y_orthogonal.transpose()<<endl);
        //Creating the rotation type
        AngleAxisd y_turn( - y_angle, y_orthogonal);
        L_DEBUG(cout<<"Turn Matrix:\n"<<(Matrix3d()<<(Matrix3d::Identity() * y_turn)).finished()<<endl);
        //rotating
        target = y_turn * target;
        if(additional_parameter > 1) {
            //same as for y-axis now for x-axis, y-axis first because of "dependencies"
            x_orthogonal = diff.cross(y_orthogonal).normalized();
            L_DEBUG(cout<<"Orthogonale:\n"<<x_orthogonal.transpose()<<endl);
            AngleAxisd x_turn(x_angle, x_orthogonal);
            L_DEBUG(cout<<"Turn Matrix:\n"<<(Matrix3d()<<(Matrix3d::Identity() * x_turn)).finished()<<endl);
            target = x_turn * target;
        }
    }
    robot.inverse_chain(ChainIds::HeadChain, target, 1e-3, 100, Kin::KJoint::AxisType::XAxis);
    L_DEBUG(cout<<"angles: y_angle:" << y_angle << " x_angle: "<< x_angle<<endl);
    L_DEBUG(cout<< "Target"<<endl<<target.transpose()<<endl);
    L_DEBUG(cout<<"Head"<<endl<<(robot.get_joint_by_id(JointIds::LFootEndpoint).get_chain_matrix_inverse() * robot.get_joint_by_id(JointIds::Camera).get_chain_matrix()).matrix()<<endl);
}

void KinematicUtil::get_head_angles_for_distance(KRobot& robot, const Vector2d& pos, bool left_leg){
    get_head_angles_for_distance_intern<0>(robot, pos, left_leg);
}
void KinematicUtil::get_head_angles_for_distance(KRobot& robot, const Vector2d& pos, bool left_leg, double y_angle){
    get_head_angles_for_distance_intern<1>(robot, pos, left_leg, y_angle);
}
void KinematicUtil::get_head_angles_for_distance(KRobot& robot, const Vector2d& pos, bool left_leg, double y_angle, double x_angle){
    get_head_angles_for_distance_intern<2>(robot, pos, left_leg, y_angle, x_angle);
}
