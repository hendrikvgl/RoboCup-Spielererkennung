#ifndef _ZMP_WALK_HPP
#define _ZMP_WALK_HPP
#include <Eigen/Core>
#include <map>
#include <string>
#include <assert.h>
#include "boost/date_time/posix_time/posix_time.hpp"
#include "zmp_walk_parameter.hpp"
#include "../robot/pose.hpp"
#include "body.hpp"
#include "../debug/debugmacro.h"
#include "../debug/debug.hpp"
#include "zmp_math_basics.h"
#include "zmp_team_darwin_kinematics.hpp"

namespace ZMPWalking{

class ZMPWalk{
public:
    typedef ZMPFootPhaseDefinition::FootPhase FootPhase;
private:

    mutable Debug::Scope m_debug;
    Eigen::Vector3d m_uTorso, m_uLeft,m_uRight;

    Eigen::Matrix<double, 6, 1> m_pLLeg, m_pRLeg, m_pTorso;

    Eigen::Vector3d m_velCurrent, m_velCommand, m_velDiff;

    struct ZMP_coeff{
        //ZMP exponential coefficients:
        double aXP=0, aXN=0, aYP=0, aYN=0, m1X=0, m2X=0, m1Y=0, m2Y=0;
    } m_ZMP_coeff;

    double m_bodyTilt;

    //Gyro stabilization variables
    double m_kneeShift;
    Eigen::Vector2d m_ankleShift, m_hipShift, m_armShift;

    bool m_active, m_started;
    int m_iStep0, m_iStep;
    boost::posix_time::ptime m_tLastStep;


    int m_stopRequest;

    int m_initial_step;

    ZMPParameter m_parameter;


    Eigen::Vector3d m_qLArm0;
    Eigen::Vector3d m_qRArm0;
    Eigen::Vector3d m_uLRFootOffset;
    double m_stanceLimitY2;


    Eigen::Vector2d m_ankleMod;

    int m_supportLeg;
    Eigen::Vector3d m_uLeft1, m_uLeft2, m_uRight1, m_uRight2, m_uTorso1, m_uTorso2;
    Eigen::Vector3d m_uTorsoActual;
    double m_shiftFactor;
    Eigen::Vector3d m_uSupport;

    Eigen::Vector3d m_imuGyr;
    Body m_body;

    std::string m_robottype;

    double m_toeTipCompensation;



public:

    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    ZMPWalk(const ZMPParameter& parameter);

    void entry();
    double get_hip_pitch(){return m_bodyTilt * rad_to_degree;}
    Robot::Pose& get_pose(){return m_body.get_pose();}
    double get_l_shoulder_pitch_offset(){return m_body.get_l_shoulder_pitch_offset();}
    double get_r_shoulder_pitch_offset(){return m_body.get_r_shoulder_pitch_offset();}
    double get_l_shoulder_roll_offset(){return m_body.get_l_shoulder_roll_offset();}
    double get_r_shoulder_roll_offset(){return m_body.get_r_shoulder_roll_offset();}
    double get_hip_pitch_offset(){return m_body.get_hip_pitch_offset();}
    std::string get_robottype(){return m_robottype;}
    const Eigen::Vector3d& get_uLeft(){return m_uLeft;}
    const Eigen::Vector3d& get_uRight(){return m_uRight;}
    const Eigen::Vector3d& get_velocity(){return m_velCurrent;}
    bool is_active(){return m_active;};
    void set_active(bool active){this->m_active = active;}
    void set_hip_pitch(double hip_pitch){m_bodyTilt = hip_pitch * degree_to_rad;}
    void set_l_shoulder_pitch_offset(double offset){m_body.set_l_shoulder_pitch_offset(offset);}
    void set_r_shoulder_pitch_offset(double offset){m_body.set_r_shoulder_pitch_offset(offset);}
    void set_l_shoulder_roll_offset(double offset){m_body.set_l_shoulder_roll_offset(offset);}
    void set_r_shoulder_roll_offset(double offset){m_body.set_r_shoulder_roll_offset(offset);}
    void set_hip_pitch_offset(double offset){m_body.set_hip_pitch_offset(offset);}
    void set_gyro_data(const Eigen::Vector3d& gyro){m_imuGyr = gyro;}
    void set_long_legs(double thigh, double tibia, double hip_y_offset, double hip_z_offset, double foot_height) {
        set_long_leg_adjusted_values(thigh, tibia, hip_y_offset, hip_z_offset, foot_height);
    }
    void set_belly_roll_pid(float p, float i, float d)
    {
    m_body.set_belly_roll_pid(p,i,d);
    }
    //set velocity ist die Walkingschnittstelle!!!
    void set_velocity(double tvx, double vy, double va);
    void set_tiltX(double tiltX, double tiltX_longTime) {m_TiltX = tiltX; if (m_TiltX != 0) m_lastTiltX = m_TiltX; m_TiltX_longTime = tiltX_longTime;}
    void set_robottype(std::string robottype){m_robottype = robottype;}
    void stance_reset();
    void start();
    void stop();
    FootPhase update();

private:

    Eigen::Vector2d foot_phase(double ph, double ph_single);
    void init_variables(const ZMPParameter& parameter);
    void load_config(const ZMPParameter& parameter);
    double mod_angle(double a);
    void motion_arms();
    void motion_legs(Eigen::Matrix<double, 12, 1>& qLegs, double phSingle);
    Eigen::Vector3d pose_global(const Eigen::Vector3d& pRelative, const Eigen::Vector3d& pose);
    Eigen::Vector3d pose_relative(const Eigen::Vector3d& uLeft1, const Eigen::Vector3d& uTorso1);
    double procFunc(double q, double s, double d);
    Eigen::Vector3d se2_interpolate(double t, const Eigen::Vector3d& u1, const Eigen::Vector3d& u2);
    Eigen::Vector3d step_left_destination(const Eigen::Vector3d& vel, const Eigen::Vector3d& uLeft, const Eigen::Vector3d& uRight);
    Eigen::Vector3d step_right_destination(const Eigen::Vector3d& vel, const Eigen::Vector3d& uLeft, const Eigen::Vector3d& uRight);
    Eigen::Vector3d step_torso(const Eigen::Vector3d& uLeft, const Eigen::Vector3d& uRight, double shiftFactor);
    void update_still(double phSingle);
    inline void calculateStepGoal();
    inline void advanceInStep(double ph, double phSingle);
    void update_velocity();
    Eigen::Vector3d zmp_com(double ph, const Eigen::Vector3d& m_uSupport,  const ZMP_coeff& zmp_coeff);
    Eigen::Vector2d zmp_solve(double zs, double z1, double z2, double x1, double x2);
    double m_TiltX, m_lastTiltX,m_TiltX_longTime;


};


}//namespace

#endif
