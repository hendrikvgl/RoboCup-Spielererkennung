#include <shm.hpp>

using namespace boost::interprocess;
using namespace Util;
using namespace IPC;
using Robot::Pose;

namespace IPC {
class IPCSyncInfo {
    public:
        IPCSyncInfo() : version(0), state(0), motion_state(0), reset_tracking(true),
            width(0), height(0){}

        long version;
        int state;
        int motion_state;
        bool button1;
        bool button2;
        Pose pose;
        DataVector<int> gyro;
        DataVector<float> robot_angle;
        DataVector<int> accel;
        DataVector<float> eye_color;
        DataVector<float> forehead_color;

        // Walking Parameter
        bool walking_activ;
        int walking_forward;
        int walking_angular;
        int walking_sidewards;

        // Tracking
        bool reset_tracking;
        int last_track_reset;
        DataVector<float> last_track;
        DataVector<float> track;
        uint8_t foot_phase;

        //image für den Simulator
        int width, height;
        char data[1024*1024*8];
};

} //namespace

SharedMemoryIPCProvider::SharedMemoryIPCProvider()
    : shm(open_or_create, "DarwinIPC", 1024 * 64  + 8*1024*1024),
      rest_mutex(*shm.find_or_construct<Mutex>("Mutex")()),
      pose_mutex(*shm.find_or_construct<Mutex>("PoseMutex")()),
      walking_mutex(*shm.find_or_construct<Mutex>("WalkingMutex")()),
      state_mutex(*shm.find_or_construct<Mutex>("StateMutex")()),
      track_mutex(*shm.find_or_construct<Mutex>("TrackMutex")()),
      info(shm.find_or_construct<IPCSyncInfo>("SyncInfo")()) {
}

void SharedMemoryIPCProvider::update(const Pose& newpose) {
    Lock lock(pose_mutex);
    info->pose.update(newpose);
    info->version += 1;
}

void SharedMemoryIPCProvider::update_positions(const Pose& newpose) {
    Lock lock(pose_mutex);
    info->pose.update_positions(newpose);
}

Robot::Pose SharedMemoryIPCProvider::get_pose() const {
    Lock lock(pose_mutex);
    return info->pose;
}

const Robot::Pose& SharedMemoryIPCProvider::get_pose_ref() const {
    Lock lock(pose_mutex);
    return info->pose;
}

long SharedMemoryIPCProvider::get_version() const {
    Lock lock(pose_mutex);
    return info->version;
}

void SharedMemoryIPCProvider::lock() {
    rest_mutex.lock();
    pose_mutex.lock();
    walking_mutex.lock();
    state_mutex.lock();
    track_mutex.lock();
}

void SharedMemoryIPCProvider::unlock() {
    rest_mutex.unlock();
    pose_mutex.unlock();
    walking_mutex.unlock();
    state_mutex.unlock();
    track_mutex.unlock();
}

void SharedMemoryIPCProvider::lock_pose() {
    pose_mutex.lock();
}

void SharedMemoryIPCProvider::unlock_pose() {
    pose_mutex.unlock();
}

void SharedMemoryIPCProvider::set_gyro(const DataVector<int>& gyro) {
    Lock lock(rest_mutex);
    info->gyro = gyro;
}

void SharedMemoryIPCProvider::set_robot_angle(const DataVector<float>& robot_angle) {
    Lock lock(rest_mutex);
    info->robot_angle = robot_angle;
}

void SharedMemoryIPCProvider::set_accel(const DataVector<int>& accel) {
    Lock lock(rest_mutex);
    info->accel = accel;
}

void SharedMemoryIPCProvider::set_button1(bool button1) {
    Lock lock(rest_mutex);
    info->button1 = button1;
}

void SharedMemoryIPCProvider::set_button2(bool button2) {
    Lock lock(rest_mutex);
    info->button2 = button2;
}

void SharedMemoryIPCProvider::set_eye_color(const DataVector<float>& dv) {
    Lock lock(rest_mutex);
    info->eye_color = dv;
}

void SharedMemoryIPCProvider::set_forehead_color(const DataVector<float>& color) {
    Lock lock(rest_mutex);
    info->forehead_color = color;
}

DataVector<int> SharedMemoryIPCProvider::get_gyro() const {
    Lock lock(rest_mutex);
    return info->gyro;
}

DataVector<float> SharedMemoryIPCProvider::get_robot_angle() const {
    Lock lock(rest_mutex);
    return info->robot_angle;
}

DataVector<int> SharedMemoryIPCProvider::get_accel() const {
    Lock lock(rest_mutex);
    return info->accel;
}

bool SharedMemoryIPCProvider::get_button1() const {
    Lock lock(rest_mutex);
    return info->button1;
}

bool SharedMemoryIPCProvider::get_button2() const {
    Lock lock(rest_mutex);
    return info->button2;
}

DataVector<float> SharedMemoryIPCProvider::get_forehead_color() const {
    Lock lock(rest_mutex);
    return info->forehead_color;
}

DataVector<float> SharedMemoryIPCProvider::get_eye_color() const {
    Lock lock(rest_mutex);
    return info->eye_color;
}

void SharedMemoryIPCProvider::set_state(int state) {
    Lock lock(state_mutex);
    info->state = state;
}

int SharedMemoryIPCProvider::get_state() const {
    Lock lock(state_mutex);
    return info->state;
}

void SharedMemoryIPCProvider::set_motion_state(int state) {
    Lock lock(state_mutex);
    info->motion_state = state;
}

int SharedMemoryIPCProvider::get_motion_state() const {
    Lock lock(state_mutex);
    return info->motion_state;
}

void SharedMemoryIPCProvider::set_walking_forward(int speed) {
    Lock lock(walking_mutex);
    info->walking_forward = speed;
}

int SharedMemoryIPCProvider::get_walking_forward() const {
    Lock lock(walking_mutex);
    return info->walking_forward;
}

void SharedMemoryIPCProvider::set_walking_foot_phase(uint8_t phase) {
    Lock lock(walking_mutex);
    info->foot_phase = phase;
}

uint8_t SharedMemoryIPCProvider::get_walking_foot_phase() const {
    Lock lock(walking_mutex);
    return info->foot_phase;
}

void SharedMemoryIPCProvider::set_walking_sidewards(int speed) {
    Lock lock(walking_mutex);
    info->walking_sidewards = speed;
}

int SharedMemoryIPCProvider::get_walking_sidewards() const {
    Lock lock(walking_mutex);
    return info->walking_sidewards;
}

void SharedMemoryIPCProvider::set_walking_angular(int speed) {
    Lock lock(walking_mutex);
    info->walking_angular = speed;
}

int SharedMemoryIPCProvider::get_walking_angular() const {
    Lock lock(walking_mutex);
    return info->walking_angular;
}

void SharedMemoryIPCProvider::set_walking_activ(bool state) {
    Lock lock(walking_mutex);
    info->walking_activ = state;
}

bool SharedMemoryIPCProvider::get_walking_activ() const {
    Lock lock(walking_mutex);
    return info->walking_activ;
}

void SharedMemoryIPCProvider::reset_tracking() const {
    Lock lock(track_mutex);
    info->reset_tracking = true;
}

bool SharedMemoryIPCProvider::get_reset_tracking() const {
    Lock lock(track_mutex);
    bool ret = info->reset_tracking;
    info->reset_tracking = false;
    return ret;
}

DataVector<float> SharedMemoryIPCProvider::get_last_track() const {
    Lock lock(track_mutex);
    return info->last_track;
}

void SharedMemoryIPCProvider::set_last_track(const DataVector<float>& track) {
    Lock lock(track_mutex);
    info->last_track = track;
}

DataVector<float> SharedMemoryIPCProvider::get_track() const {
    Lock lock(track_mutex);
    return info->track;
}

void SharedMemoryIPCProvider::set_track(const DataVector<float>& track) {
    Lock lock(track_mutex);
    info->track = track;
}

int SharedMemoryIPCProvider::get_last_track_time() const {
    Lock lock(track_mutex);
    return info->last_track_reset;
}

void SharedMemoryIPCProvider::set_last_track_time(const int time) {
    Lock lock(track_mutex);
    info->last_track_reset = time;
}

void SharedMemoryIPCProvider::set_image(int width, int height, const char *data) {
    Lock lock(rest_mutex);
    info->width = width;
    info->height = height;

    std::copy(data, data + width*height*3, info->data);
}

char* SharedMemoryIPCProvider::get_image() const {
    Lock lock(rest_mutex);
    char* data = new char[info->width*info->height*3+10];
    std::copy(info->data, info->data + info->width*info->height*3, data);
    return data;
}

int SharedMemoryIPCProvider::get_image_width() const {
    Lock lock(rest_mutex);
    return info->width;
}

int SharedMemoryIPCProvider::get_image_height() const {
    Lock lock(rest_mutex);
    return info->height;
}
