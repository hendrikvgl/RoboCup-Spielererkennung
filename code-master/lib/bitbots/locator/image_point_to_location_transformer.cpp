#include <cmath>
#include <Eigen/Core>
#include <vector>
#include <array>

#include "image_point_to_location_transformer.hpp"
#include "../robot/kinematic_robot.hpp"
#include "../robot/jointids.hpp"
#include "../debug/debug.hpp"

using namespace Location;
using namespace Eigen;
using namespace std;
typedef Robot::Kinematics::JointIds J;

//transform und transform_point sind im header, damit das inlining funktioniert


double Image_Point_To_Location_Transformer::get_ray_motor_distance(const Vector2d& image_point) {
    Vector3d ray(1, image_point.x() * m_camera_angle_factor, image_point.y() * m_camera_angle_factor);
    const static array<J, 7> ids_to_check({{J::RShoulderPitch, J::LShoulderPitch, J::RShoulerRoll, J::LShoulderRoll, J::RKnee, J::LKnee, J::Neck}});
    const Affine3d cam_inverse = robot[J::Camera].get_chain_matrix_inverse();
    //const Vector3d ray_start = Vector3d::Zero();
    double result = (double)((unsigned)-1);

    for(J id: ids_to_check) {
        Vector3d motor_endpoint = (cam_inverse * robot[id].get_chain_matrix()).translation();
        Vector3d distance = motor_endpoint.cross(ray.normalized());
        result = std::min(distance.norm(), result);
        motor_endpoint.x() -= 0.03;
        distance = motor_endpoint.cross(ray.normalized());
        result = std::min(distance.norm(), result);
    }
    const static array<J, 2> ids_to_check2({{J::RShoulderPitch, J::LShoulderPitch}});
    for(J id: ids_to_check2) {
        Vector3d motor_endpoint = (cam_inverse * robot[id].get_chain_matrix()).translation();
        motor_endpoint.x() -= 0.06;
        Vector3d distance = motor_endpoint.cross(ray.normalized());
        result = std::min(distance.norm(), result);
    }
    return result;
}

Matrix4f create_floor_matrix(const Robot::Kinematics::KRobot& robot) {
    Matrix4f to_floor(Matrix4f::Identity());
    to_floor.col(3).head<3>()<<0,0,-0.01;
    to_floor = to_floor * robot[J::Camera].get_chain_matrix().matrix().cast<float>();
    return to_floor;
}

/*
 * ccw Winkelmethode aus der Masterarbeit. Überpüft, ob der von den drei Parametervektoren eingeschlossene Winkel im oder gegen
 * den Uhrzeigersinn läuft. Keine Ahnung ob + oder - für im Uhrzeigersinn steht.
 */
template<class T>
inline T ccw(T v_0x, T v_0y, T v_1x, T v_1y, T v_2x, T v_2y)
{
    return (v_1x - v_0x) * (v_2y - v_0y) - (v_2x - v_0x) * (v_1y - v_0y);
}
template<class T>
inline T ccw(const Matrix<T,2,1>& v_0, const Matrix<T,2,1>& v_1, const Matrix<T,2,1>& v_2)
{
    //std::cout<<"Das was gestetet wird: \n"<<(Eigen::Matrix<T, 3, 2>()<<v_0.transpose(), v_1.transpose(), v_2.transpose()).finished();//<<std::endl;
    T res = ccw(v_0.x(), v_0.y(), v_1.x(), v_1.y() ,v_2.x(), v_2.y());
    //std::cout<<"\tResult: "<<res<<std::endl;
    return res;
}

vector<bool> Image_Point_To_Location_Transformer::convex_hull(const Matrix2Xf& image_points) {
    Matrix4f to_floor_ = create_floor_matrix(robot);
    Matrix2Xf plane_hits(2, image_points.cols());
    for(int i = 0; i < image_points.cols(); ++i) {
        plane_hits.col(i) = transform(image_points.col(i), to_floor_.col(3), to_floor_);
    }
    // Now shift the fount points, so that the distance corresponds to the distance from the root joint
    plane_hits.colwise() += robot[J::Camera].get_endpoint<2>().cast<float>();
    Matrix<float, 2, 6>/*Matrix2Xi*/ convex_hull(2, 6);
    #define V2f Vector2f
    convex_hull<<V2f(-25,100), V2f(30,100), V2f(30,-100), V2f(-25, -100), V2f(-80,-65),V2f(-80,65);
    #undef V2f
    convex_hull /= 1000;
    vector<bool> result;
    result.reserve(image_points.cols());
    for(int i = 0; i < image_points.cols(); ++i) {
        for(int j = 0; j < convex_hull.cols(); ++j) {
            if(ccw<float>(convex_hull.col(j), convex_hull.col((j + 1)%convex_hull.cols()), plane_hits.col(i)) >= 0) {
                result.push_back(false);
                break;
            }
        }
        // If we havn't added a true, then we can add a false to the results now
        if(i == result.size())
            result.push_back(true);
    }
    /*std::cout<<"Zusammenfasung:\nHead: "<<to_floor_.col(3).transpose()<<
                "\n to_floor:\n"<<to_floor_<<
                "\n plane_hits: "<<plane_hits.transpose()<<
                "\n Motorwinkel: 19: "<<robot[19].get_angle()<<
                "\n Motorwinkel: 20: "<<robot[20].get_angle()<<std::endl;*/
    return result;
}

Vector2f Image_Point_To_Location_Transformer::transform_point_with_offset(
    const Vector2f& normalized_image_point, float z_offset)
{
    //std::cout<<"Transformer in: "<< normalized_image_point.transpose()<<" z: "<<z_offset<<std::endl;
    Vector2f result = transform(normalized_image_point,
        head - Vector4f(0,0,z_offset,0));
    //std::cout<<"Leg inverse\n"<<robot[Robot::Kinematics::JointIds::LFootEndpoint].get_chain_matrix_inverse().matrix()<<std::endl;
    //astd::cout<<"To to_floor\n"<<to_floor<<std::endl;
    //std::cout<<"Transformer out "<<result.transpose()<<std::endl;
    return result;
}

int Image_Point_To_Location_Transformer::set_floor_matrix_and_head(){
    Matrix4f result;

    // Referenzen auf die gespeicherten Matrizen holen (Körper zum Fuss)
    const Matrix4f& leg_l = robot.get_joint_by_id(J::LFootEndpoint).get_chain_matrix().matrix().cast<float>();
    const Matrix4f& leg_r = robot.get_joint_by_id(J::RFootEndpoint).get_chain_matrix().matrix().cast<float>();

    // Inverse zu den Matritzen berechnen (Fuss zum Körper)
    Matrix4f leg_l_inv = robot.get_joint_by_id(J::LFootEndpoint).get_chain_matrix_inverse().matrix().cast<float>();
    Matrix4f leg_r_inv = robot.get_joint_by_id(J::RFootEndpoint).get_chain_matrix_inverse().matrix().cast<float>();

    DEBUG(5, "LHipHigh", leg_l_inv.row(2)(3));
    DEBUG(5, "RHipHigh", leg_r_inv.row(2)(3));
    // Höhendifferenz zwischen Fussebene links zum rechten Fuss
    // und zwischen rechter Fussebene und linkem Fuss
    float l_to_r = (leg_l_inv * leg_r)(2,3);
    float r_to_l = (leg_r_inv * leg_l)(2,3);

    int definite_position;
    if(l_to_r > 0 and r_to_l < 0) {
        result = leg_l_inv;
        definite_position = 1;
        DEBUG(5, "Bein", "links");
    } else
    if(r_to_l > 0 and l_to_r < 0) {
        result = leg_r_inv;
        definite_position = -1;
        DEBUG(5, "Bein", "rechts");
    } else {

        // Wir wissen nicht, auf welchem Fuss der Roboter steht.
        //DEBUG_LOG(NEW_FEATURE,"Kann nicht genau sagen, auf welchem Fuss der Roboter steht");
        //DEBUG(NEW_FEATURE, "Bein", "links");
        result = leg_l_inv;
        definite_position = 0;
    }

    // y-Mittelachse des Roboters verschieben
    result(1, 3) = 0;
    to_floor = result*robot[J::Camera].get_chain_matrix().matrix().cast<float>();
    head = result * robot[J::Camera].get_endpoint().matrix().cast<float>();// Position der Kamera
    DEBUG(INFO, "CameraHeight", head(2));
    //DEBUG_LOG(INFO, "to_floor Matrix\n"<<to_floor<<"\n");
    //cout<<"to_floor Matrix\n"<<to_floor<<"\n";

    return definite_position;
}
