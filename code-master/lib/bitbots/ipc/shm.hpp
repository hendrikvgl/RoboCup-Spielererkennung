#ifndef _SHM_HPP
#define _SHM_HPP

#include "ipcprovider.hpp"

#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/sync/interprocess_recursive_mutex.hpp>
#include <boost/interprocess/sync/scoped_lock.hpp>

namespace IPC {

using Util::DataVector;
class IPCSyncInfo;

/**
 * This is a shared memory IPC.
 * We use this class for our inter process communication writing into a file
 * laying in /dev/shm.
 * This SharedMemoryIPCProvider holds a info struct that really is accessible
 * from the different processes.
 * Usually only the motion and the main behaviour use the IPC, but some of our tool
 * use it to communicate with the motion, too. But not during the games.
 */
class SharedMemoryIPCProvider : public IPCProvider {
    private:
        typedef boost::interprocess::interprocess_recursive_mutex Mutex;
        typedef boost::interprocess::scoped_lock<Mutex> Lock;

        boost::interprocess::managed_shared_memory shm;
        Mutex &rest_mutex, &pose_mutex, &walking_mutex, &state_mutex, &track_mutex;

        IPCSyncInfo *info;

    public:

        SharedMemoryIPCProvider();
        virtual void lock();
        virtual void unlock();
        virtual void lock_pose();
        virtual void unlock_pose();

        virtual long get_version() const;

        virtual Robot::Pose get_pose() const;
        virtual const Robot::Pose& get_pose_ref() const;
        virtual void update(const Robot::Pose& pose);
        virtual void update_positions(const Robot::Pose& pose);

        virtual DataVector<int> get_gyro() const;
        virtual void set_gyro(const DataVector<int>& data);

        virtual DataVector<float> get_robot_angle() const;
        virtual void set_robot_angle(const DataVector<float>& data);

        virtual DataVector<int> get_accel() const;
        virtual void set_accel(const DataVector<int>& data);

        virtual bool get_button1() const;
        virtual void set_button1(bool data);

        virtual bool get_button2() const;
        virtual void set_button2(bool data);

        virtual int get_state() const;
        virtual void set_state(int state);

        virtual int get_motion_state() const;
        virtual void set_motion_state(int state);

        virtual DataVector<float> get_eye_color() const;
        virtual void set_eye_color(const DataVector<float>& color);

        virtual DataVector<float> get_forehead_color() const;
        virtual void set_forehead_color(const DataVector<float>& color);

        //walking
        virtual void set_walking_forward(int speed);
        virtual int get_walking_forward() const;

        virtual void set_walking_sidewards(int speed);
        virtual int get_walking_sidewards() const;

        virtual void set_walking_angular(int speed);
        virtual int get_walking_angular() const;

        virtual void set_walking_activ(bool state);
        virtual bool get_walking_activ() const;

        virtual void set_walking_foot_phase(uint8_t phase);
        virtual uint8_t get_walking_foot_phase() const;

        //tracking
        virtual void reset_tracking() const;
        virtual bool get_reset_tracking() const;

        virtual DataVector<float> get_last_track() const;
        virtual void set_last_track(const DataVector<float>& track);

        virtual DataVector<float> get_track() const;
        virtual void set_track(const DataVector<float>& track);

        virtual int get_last_track_time() const;
        virtual void set_last_track_time(const int time);

        //simulator
        virtual char* get_image() const;
        virtual int get_image_height() const;
        virtual int get_image_width() const;
        virtual void set_image(int width, int height, const char *data);

};

} //namespace

#endif
