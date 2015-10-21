from bitbots.robot.pose cimport Pose
from bitbots.util.datavector cimport DataVector, IntDataVector
from libcpp cimport bool
from libcpp.string cimport string

cdef import from "ipcprovider.hpp":
    cdef cppclass IPCProvider "IPC::IPCProvider":
        void lock()
        void unlock()
        void lock_pose()
        void unlock_pose()

        long get_version()

        # eigentlich const Pose&
        Pose& get_pose_ref()
        Pose get_pose()

        void update(Pose& pose)
        void update_positions(Pose& pose)

        IntDataVector get_gyro()
        void set_gyro(IntDataVector& gyro)

        DataVector get_robot_angle()
        void set_robot_angle(DataVector& gyro)

        IntDataVector get_accel()
        void set_accel(IntDataVector& accel)

        DataVector get_eye_color()
        void set_eye_color(DataVector& color)

        DataVector get_forehead_color()
        void set_forehead_color(DataVector& color)

        int get_state()
        void set_state(int state)

        bool get_button1()
        void set_button1(bool button1)

        bool get_button2()
        void set_button2(bool button2)

        int get_motion_state()
        void set_motion_state(int state)

        void set_walking_forward(int speed)
        int get_walking_forward()

        void set_walking_sidewards(int speed)
        int get_walking_sidewards()

        void set_walking_angular(int speed)
        int get_walking_angular()

        void set_walking_activ(bool state)
        bool get_walking_activ()

        void set_walking_foot_phase(unsigned char phase)
        unsigned char get_walking_foot_phase()

        void reset_tracking()
        bool get_reset_tracking()

        DataVector get_last_track()
        void set_last_track(DataVector& track)

        DataVector get_track()
        void set_track(DataVector& track)

        int get_last_track_time()
        void set_last_track_time(int time)

        char* get_image()
        int get_image_width()
        int get_image_height()
        void set_image(int width, int height, char *data)


cdef import from "shm.hpp":
    cdef cppclass SharedMemoryIPCProvider "IPC::SharedMemoryIPCProvider":
        pass

