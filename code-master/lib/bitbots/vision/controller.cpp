#include "controller.hpp"
#include "capture.hpp"

using namespace Vision::Video;

Controller::~Controller() {}

float Controller::get_default() const { return 0; }

std::string Controller::get_name() const { return "not supported"; }

float Controller::get_value() const { return 0; }

int Controller::get_value_raw() const { return 0; }

void Controller::set_value(float v __attribute__((unused))) {
    std::clog << "Setting this value is not supported: " << get_name()
              << std::endl;
}

void Controller::set_bool(bool on) { set_value(on ? 1.f : 0.f); }

void Controller::set_value_raw(int value __attribute__((unused))) {
    std::clog << "Setting this value is not supported" << std::endl;
}

float RealController::to_float(int v) const {
    return (float(v) - info.minimum) / (info.maximum - info.minimum);
}

int RealController::to_int(float v) const {
    return v * (info.maximum - info.minimum) + info.minimum;
}

float RealController::get_value() const {
    return to_float(get_value_raw());
}

int RealController::get_value_raw() const {
    auto ctrl = v4l2_control{};
    ctrl.id = info.id;
    capture.ioctl(VIDIOC_G_CTRL, ctrl);
    return ctrl.value;
}

void RealController::set_value(float value) {
    assert(value >= 0 && value <= 1);
    set_value_raw(to_int(value));
}

void RealController::set_value_raw(int value) {
    auto ctrl = v4l2_control{};
    ctrl.id = info.id;
    ctrl.value = value;
    capture.ioctl(VIDIOC_S_CTRL, ctrl);
}

void RealController::set_bool(bool on) { set_value_raw(int{on}); }

std::ostream & operator<<(std::ostream & out, const Controller & ctrl) {
    out << "<" << ctrl.get_name() << ": " << ctrl.get_value() << ">";
    return out;
}
