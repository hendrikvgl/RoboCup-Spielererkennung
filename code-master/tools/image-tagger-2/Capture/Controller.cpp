#include "Controller.hpp"

Controller::Controller(int fd)
{
    // Check whether the given file descriptor is valid.
    if(fcntl(fd, F_GETFL) == -1)
	throw ControllerException("Bad file descriptor.");

    fd_ = fd;
}

Controller::~Controller() = default;

template <typename T> inline
T getValueFromCamera(int fd, int controller, const std::string& name)
{
    v4l2_control control = { };
    control.id = controller;
    if(ioctl(fd, VIDIOC_G_CTRL, &control) == -1)
        throw ControllerException(std::string("Unable to get controller value: ") + name);

    return control.value;
}

inline
int Controller::intRequest(int controller, const std::string& name) const
{
    // Request the value of the given camera property and returns it as an
    // integer.
    return getValueFromCamera<int>(fd_, controller, name);
}

inline
bool Controller::boolRequest(int controller, const std::string& name) const
{
    // Request the value of the given camera property and returns it as an
    // boolean.
    return getValueFromCamera<bool>(fd_, controller, name);
}

inline
void Controller::intChange(int controller, int value, const std::string& name)
{
    v4l2_queryctrl queryctrl = { };
    v4l2_control control = { };

    // Check whether the operation is supported.
    queryctrl.id = controller;
    if(ioctl(fd_, VIDIOC_QUERYCTRL, &queryctrl) == -1)
        throw ControllerException(std::string("Controller not supported: ") + name);

    control.id = controller;
    control.value = value;

    // Set the new value.
    if(ioctl(fd_, VIDIOC_S_CTRL, &control))
        throw ControllerException(std::string("Controller value was not changed: ") + name);
}

inline
void Controller::boolChange(int controller, bool value, const std::string& name)
{
    v4l2_queryctrl queryctrl = { };
    v4l2_control control = { };

    // Check whether the operation is supported.
    queryctrl.id = controller;
    if(ioctl(fd_, VIDIOC_QUERYCTRL, &queryctrl) == -1)
        throw ControllerException(std::string("Controller not supported: ") + name);

    control.id = controller;
    control.value = value;

    // Set the new value.
    if(ioctl(fd_, VIDIOC_S_CTRL, &control))
        throw ControllerException(std::string("Controller value was not changed: ") + name);
}

int Controller::getBrightness() const
{
    return intRequest(V4L2_CID_BRIGHTNESS, "Brightness");
}

int Controller::getContrast() const
{
    return intRequest(V4L2_CID_CONTRAST, "Contrast");
}

int Controller::getSaturation() const
{
    return intRequest(V4L2_CID_SATURATION, "Saturation");
}

int Controller::getHue() const
{
    return intRequest(V4L2_CID_HUE, "Hue");
}

int Controller::getSharpness() const
{
    return intRequest(V4L2_CID_SHARPNESS, "Sharpness");
}

int Controller::getGain() const
{
    return intRequest(V4L2_CID_GAIN, "Gain");
}

int Controller::getWhiteBalanceTemperature() const
{
    return intRequest(V4L2_CID_WHITE_BALANCE_TEMPERATURE, "WhiteBalance");
}

int Controller::getFocusAbsolute() const
{
    return intRequest(V4L2_CID_FOCUS_ABSOLUTE, "Focus Absolute");
}

int Controller::getFocusRelative() const
{
    return intRequest(V4L2_CID_FOCUS_RELATIVE, "Focus Relative");
}

int Controller::getExposureAbsolute() const
{
    return intRequest(V4L2_CID_EXPOSURE_ABSOLUTE, "Exposure Absolute");
}

bool Controller::isExposureAutoPriorityOn() const
{
    return boolRequest(V4L2_CID_EXPOSURE_AUTO_PRIORITY, "Exposure Auto");
}

bool Controller::isAutoGainOn() const
{
    return boolRequest(V4L2_CID_AUTOGAIN, "Auto Gain");
}

bool Controller::isAutoWhiteBalanceOn() const
{
    return boolRequest(V4L2_CID_AUTO_WHITE_BALANCE, "Auto White Balance");
}

bool Controller::isFocusAutoOn() const
{
    return boolRequest(V4L2_CID_FOCUS_AUTO, "Focus Auto");
}

bool Controller::isExposureAutoOn() const
{
    return boolRequest(V4L2_CID_EXPOSURE_AUTO, "Exposure Auto");
}

void Controller::setBrigthness(int value)
{
    intChange(V4L2_CID_BRIGHTNESS ,value, "Brightness");
}

void Controller::setContrast(int value)
{
    intChange(V4L2_CID_CONTRAST ,value, "Contrast");
}

void Controller::setSaturation(int value)
{
    intChange(V4L2_CID_SATURATION ,value, "Saturation");
}

void Controller::setHue(int value)
{
    intChange(V4L2_CID_HUE ,value, "Hue");
}

void Controller::setSharpness(int value)
{
    intChange(V4L2_CID_SHARPNESS ,value, "Sharpness");
}

void Controller::setGain(int value)
{
    intChange(V4L2_CID_GAIN ,value, "Gain");
}

void Controller::toggleAutoGainOn(bool value)
{
    intChange(V4L2_CID_AUTOGAIN ,value, "Auto Gain");
}

void Controller::toggleAutoWhiteBalanceOn(bool value)
{
    boolChange(V4L2_CID_AUTO_WHITE_BALANCE ,value, "Auto White Balance");
}

void Controller::setWhiteBalanceTemperature(int value)
{
    intChange(V4L2_CID_WHITE_BALANCE_TEMPERATURE ,value, "White Balance Temperature");
}

void Controller::setFocusAbsolute(int value)
{
    intChange(V4L2_CID_FOCUS_ABSOLUTE ,value, "Focus Absolute");
}

void Controller::setFocusRelative(int value)
{
    intChange(V4L2_CID_FOCUS_RELATIVE ,value, "Focus Relative");
}

void Controller::toggleFocusAuto(bool value)
{
    boolChange(V4L2_CID_FOCUS_AUTO ,value, "Focus Auto");
}
void Controller::toggleExposureAuto(bool value)
{
    boolChange(V4L2_CID_EXPOSURE_AUTO ,value, "Exposure Auto");
}

void Controller::setExposureAbsolute(int value)
{
    intChange(V4L2_CID_EXPOSURE_ABSOLUTE ,value, "Exposure Absolute");
}

void Controller::toggleExposureAutoPriority(bool value)
{
    boolChange(V4L2_CID_EXPOSURE_AUTO_PRIORITY ,value, "Exposure Auto Priority");
}
