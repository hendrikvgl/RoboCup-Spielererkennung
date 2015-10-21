#ifndef BITBOTS_VISION_CONTROLLER_HPP
#define BITBOTS_VISION_CONTROLLER_HPP

#include <linux/videodev2.h>
#include <string>
#include <boost/utility.hpp>

namespace Vision {
namespace Video {

class VideoCapture;
class Controller : boost::noncopyable {
public:
    virtual ~Controller();

    virtual float get_default() const;

    virtual std::string get_name() const;

    virtual float get_value() const;

    virtual int get_value_raw() const;

    virtual void set_value(float v __attribute__((unused)));

    virtual void set_bool(bool on);

    virtual void set_value_raw(int value __attribute__((unused)));
};

class RealController : public Controller {
public:
    RealController(VideoCapture & capture, const v4l2_queryctrl & info)
        : capture(capture), info(info) {}

    float get_default() const { return to_float(info.default_value); }

    std::string get_name() const {
        return {reinterpret_cast<const char *>(+info.name)};
    }

    float get_value() const;
    int get_value_raw() const;

    void set_bool(bool on);
    void set_value(float value);
    void set_value_raw(int value);

private:
    VideoCapture & capture;
    v4l2_queryctrl info;

    inline float to_float(int value) const;
    inline int to_int(float value) const;
};

std::ostream & operator<<(std::ostream &, const Controller &);

}
}

#endif
