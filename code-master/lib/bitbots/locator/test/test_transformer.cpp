#include <iostream>
#include <Eigen/Core>
#include <gtest/gtest.h>
#include <memory>

#include "../image_point_to_location_transformer.hpp"
#include "../../robot/kinematic_robot.hpp"

#ifndef YAML_NOTFOUND

using namespace Eigen;
using namespace std;
using namespace Robot;
using namespace Kinematics;
using namespace Location;

namespace Test {

#define ASSERT_EQ_(expected, actual) ASSERT_EQ(expected, actual)<< "But was:"<<endl<< actual<< endl<<"instead of"<<endl<<expected
#define EXPECT_EQ_(expected, actual) EXPECT_EQ(expected, actual)<< "But was:"<<endl<< actual<< endl<<"instead of"<<endl<<expected

TEST(Transformer, MotorPointDistance) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(-90);
    p.get_head_tilt().set_position(-90);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    double dist = transformer.get_ray_motor_distance(Vector2d(0,0));
    EXPECT_NEAR(dist, 0.0043, 0.0001);
    //EXPECT_DOUBLE_EQ(dist, 0);
}

TEST(Transformer, MotorPointDistance2) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(90);
    p.get_head_tilt().set_position(-90);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    double dist = transformer.get_ray_motor_distance(Vector2d(0,0));
    EXPECT_NEAR(dist, 0.0043, 0.0001);
    //EXPECT_DOUBLE_EQ(dist, 0);
}

TEST(Transformer, MotorPointDistance3) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(0);
    p.get_head_tilt().set_position(-90);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    double dist = transformer.get_ray_motor_distance(Vector2d(0,0));
    EXPECT_NEAR(dist, 0.0561, 0.0001);
    //EXPECT_DOUBLE_EQ(dist, 0);
}

TEST(Transformer, MotorPointDistance4) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(0);
    p.get_head_tilt().set_position(0);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    double dist = transformer.get_ray_motor_distance(Vector2d(0,0));
    EXPECT_NEAR(dist, 0.0939, 0.0001);
    //EXPECT_DOUBLE_EQ(dist, 0);
}

TEST(Transformer, MotorPointDistance5) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(120);
    p.get_head_tilt().set_position(90);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    double dist = transformer.get_ray_motor_distance(Vector2d(0,0));
    EXPECT_NEAR(dist, 0.0234, 0.0001);
    //EXPECT_DOUBLE_EQ(dist, 0);
}

TEST(Transformer, ConvexHull) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(90);
    p.get_head_tilt().set_position(90);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    std::vector<bool> inside = transformer.convex_hull(Vector2f(0,0));
    EXPECT_TRUE(inside[0]);
}

TEST(Transformer, ConvexHull2) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(0);
    p.get_head_tilt().set_position(0);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    std::vector<bool> inside = transformer.convex_hull(Vector2f(0,0));
    EXPECT_FALSE(inside[0]);
}

TEST(Transformer, ConvexHull3) {
    unique_ptr<KRobot> robot_ptr(load_robot_from_file());
    Pose p;
    p.get_head_pan().set_position(1);
    p.get_head_tilt().set_position(1);
    robot_ptr->update(p);
    Image_Point_To_Location_Transformer transformer(*robot_ptr);
    std::vector<bool> inside = transformer.convex_hull(Vector2f(0.001,0));
    EXPECT_FALSE(inside[0]);
}

} //namespace Test
using namespace ::Test;
#endif

int main(int argc, char** argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
