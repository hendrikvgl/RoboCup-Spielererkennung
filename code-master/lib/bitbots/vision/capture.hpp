#ifndef _VIDEO_CAPTURE_HPP
#define _VIDEO_CAPTURE_HPP

#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>

#include <iostream>

#include <linux/videodev2.h>

#include <vector>
#include <map>
#include <string>
#include <memory>

#include <boost/system/system_error.hpp>

#include "buffer.hpp"
#include "controller.hpp"

#include "image_decoder.hpp"
#include "../util/eigen_util.hpp"

namespace Vision {
namespace Video {

/**
 *  Exception-Klasse für Fehler
 */
class VideoError : public boost::system::system_error {
public:
    VideoError(const std::string & desc)
        : system_error(errno, boost::system::get_generic_category(), desc) {}
};

/**
 * The video capture is responsible for accessing the camera
 */
class VideoCapture {
public:
    VideoCapture();
    ~VideoCapture();

    VideoCapture(std::string device);
    void open(std::string device);

    int get_fd() const;

    void set_max_fps(unsigned int fps) { max_fps = fps; }

    void start();

    void set_pixel_format(std::string fmt, int width, int height);

    template <class T>
    bool ioctl(int request, T & data, bool quiet = false) const {
        int rc = ::ioctl(fd, request, (void *)&data);
        if (!quiet && rc == -1) {
            throw VideoError(std::string("ioctl faild: ") +
                             std::string(strerror(errno)) + std::string(" (") +
                             std::to_string(errno) + std::string(")"));
        }
        return rc != -1;
    }

    const std::string & get_pixel_format() const { return format; }

    int get_width() const { return width; }

    int get_height() const { return height; }

    template <class T> void set_image_decoder() {
        decoder = std::make_shared<T>(width, height);
    }

    using PixelFormatList = std::vector<std::pair<std::string, std::string>>;
    PixelFormatList enumerate_pixel_formats();

    Controller & get_brightness() { return *controllers[V4L2_CID_BRIGHTNESS]; }

    Controller & get_contrast() { return *controllers[V4L2_CID_CONTRAST]; }

    Controller & get_saturation() { return *controllers[V4L2_CID_SATURATION]; }

    Controller & get_hue() { return *controllers[V4L2_CID_HUE]; }

    Controller & get_sharpness() { return *controllers[V4L2_CID_SHARPNESS]; }

    Controller & get_gain() { return *controllers[V4L2_CID_GAIN]; }

    Controller & get_gain_auto() { return *controllers[V4L2_CID_AUTOGAIN]; }

    Controller & get_white_balance_temperature() {
        return *controllers[V4L2_CID_WHITE_BALANCE_TEMPERATURE];
    }

    Controller & get_white_balance_temperature_auto() {
        return *controllers[V4L2_CID_AUTO_WHITE_BALANCE];
    }

    Controller & get_exposure_auto() {
        return *controllers[V4L2_CID_EXPOSURE_AUTO];
    }

    Controller & get_exposure_auto_priority() {
        return *controllers[V4L2_CID_EXPOSURE_AUTO_PRIORITY];
    }

    Controller & get_exposure_absolute() {
        return *controllers[V4L2_CID_EXPOSURE_ABSOLUTE];
    }

    Controller & get_focus_absolute() {
        return *controllers[V4L2_CID_FOCUS_ABSOLUTE];
    }

    Controller & get_focus_relative() {
        return *controllers[V4L2_CID_FOCUS_RELATIVE];
    }

    Controller & get_focus_auto() { return *controllers[V4L2_CID_FOCUS_AUTO]; }

    Controller & get_controller(const std::string & name);

    Eigen::MapRMatb * grab();

private:
    unsigned max_fps = 25;

    int fd;
    std::vector<std::shared_ptr<Buffer>> buffers;
    std::map<int, std::shared_ptr<Controller>> controllers;

    int width, height;
    std::string format;
    std::shared_ptr<Decoder::ImageDecoder> decoder;

    Buffer & dequeue();
    void request_buffers();
    void initialize_controllers();
};

}
} // namespace

#endif

