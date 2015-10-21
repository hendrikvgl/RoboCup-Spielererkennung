#ifndef _ICP_PROVIDER_HPP
#define _ICP_PROVIDER_HPP

#include <utility>
#include "pose.hpp"
#include "../util/datavector.hpp"

namespace IPC {

using Util::DataVector;

/**
 * \brief The IPC our process communication interface.
 *
 * This is the communication interface for our software. Currently we are running two
 * independent processes for the motion and the main behaviour.
 * These two processes communicate using this IPC implementation.
 */
class IPCProvider {
    public:

        virtual ~IPCProvider() {};

        virtual void lock() = 0;
        virtual void unlock() = 0;
        virtual void lock_pose() = 0;
        virtual void unlock_pose() = 0;

        virtual long get_version() const = 0;

        /**
         * We want to copy the pose each time to avoid race conditins
         */
        virtual Robot::Pose get_pose() const = 0;
        virtual const Robot::Pose& get_pose_ref() const = 0;
        virtual void update(const Robot::Pose& pose) = 0;
        virtual void update_positions(const Robot::Pose& pose) = 0;

        virtual DataVector<int> get_gyro() const = 0;
        virtual void set_gyro(const DataVector<int>& data) = 0;

        virtual DataVector<float> get_robot_angle() const = 0;
        virtual void set_robot_angle(const DataVector<float>& data) = 0;

        virtual DataVector<int> get_accel() const = 0;
        virtual void set_accel(const DataVector<int>& data) = 0;

        virtual int get_state() const = 0;
        virtual void set_state(int state) = 0;

        virtual bool get_button1() const = 0;
        virtual void set_button1(bool state) = 0;

        virtual bool get_button2() const = 0;
        virtual void set_button2(bool state) = 0;

        virtual int get_motion_state() const = 0;
        virtual void set_motion_state(int state) = 0;

        virtual DataVector<float> get_eye_color() const = 0;
        virtual void set_eye_color(const DataVector<float>& color) = 0;

        virtual DataVector<float> get_forehead_color() const = 0;
        virtual void set_forehead_color(const DataVector<float>& color) = 0;

        virtual void set_walking_forward(int speed) = 0;
        virtual int get_walking_forward() const = 0;

        virtual void set_walking_sidewards(int speed) = 0;
        virtual int get_walking_sidewards() const = 0;

        virtual void set_walking_angular(int speed) = 0;
        virtual int get_walking_angular() const = 0;

        virtual void set_walking_activ(bool state) = 0;
        virtual bool get_walking_activ() const = 0;

        virtual void set_walking_foot_phase(uint8_t phase) = 0;
        virtual uint8_t get_walking_foot_phase() const = 0;

        virtual void reset_tracking() const = 0 ;
        virtual bool get_reset_tracking() const = 0;

        virtual DataVector<float> get_last_track() const  = 0;
        virtual void set_last_track(const DataVector<float>& track) = 0;

        virtual DataVector<float> get_track() const = 0;
        virtual void set_track(const DataVector<float>& track) = 0;

        virtual int get_last_track_time() const = 0;
        virtual void set_last_track_time(const int time) = 0;

        virtual void set_image(int width, int height, const char *data) = 0;
        virtual char* get_image() const = 0;
        virtual int get_image_width() const = 0;
        virtual int get_image_height() const = 0;
};

} //namespace

#endif

