#include <cstdlib>
#include <cerrno>

#include <sys/mman.h>
#include <utility>

#include "capture.hpp"

#include "debug.hpp"
#include "../debug/debugmacro.h"
static Debug::Scope m_debug("Camera");

using namespace Vision;
using namespace Vision::Video;


VideoCapture::VideoCapture() : fd(-1), width(-1), height(-1) {}

VideoCapture::VideoCapture(std::string device) : fd(-1), width(-1), height(-1) {

    open(std::move(device));
}

VideoCapture::~VideoCapture() {
    if (fd == -1)
        ::close(fd);
}

void VideoCapture::open(std::string device) {
    fd = ::open(device.c_str(), O_RDWR);
    if (fd == -1) {
        throw VideoError("Opening capture device");
    }

    auto caps = v4l2_capability{};
    ioctl(VIDIOC_QUERYCAP, caps);

    const auto pixelFormatList = enumerate_pixel_formats();
    for (int i = 0; i < pixelFormatList.size(); i++) {
        DEBUG_LOG(2, "PixelFormat" << pixelFormatList[i].first << ":"
                                   << pixelFormatList[i].second);
    }

    initialize_controllers();
}

int VideoCapture::get_fd() const { return fd; }

void VideoCapture::set_pixel_format(std::string fmt, int newWidth,
                                    int newHeight) {
    if (fmt.size() != 4) {
        throw std::runtime_error(
            "Captain obvious: fourcc must be four chars long");
    }

    auto formatSettings = v4l2_format{};
    formatSettings.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

    ioctl(VIDIOC_G_FMT, formatSettings);

    formatSettings.fmt.pix.width = newWidth;
    formatSettings.fmt.pix.height = newHeight;
    formatSettings.fmt.pix.field = V4L2_FIELD_NONE;
    formatSettings.fmt.pix.pixelformat =
        v4l2_fourcc(fmt[0], fmt[1], fmt[2], fmt[3]);

    ioctl(VIDIOC_S_FMT, formatSettings);

    width = formatSettings.fmt.pix.width;
    height = formatSettings.fmt.pix.height;
    format = fmt;

    if (fmt != format) {
        std::cerr << "Could not set PixelFormat " << fmt << " it's still "
                  << format << " resolution: " << width << "x" << height
                  << std::endl;
        DEBUG_LOG(0, "Could not set PixelFormat " << fmt << " it's still "
                                                  << format);
        abort();
    }

    auto parm = v4l2_streamparm{};
    parm.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

    ioctl(VIDIOC_G_PARM, parm);
    if (parm.parm.capture.capability & V4L2_CAP_TIMEPERFRAME) {
        parm.parm.capture.timeperframe.numerator = 1;
        parm.parm.capture.timeperframe.denominator = max_fps;
        ioctl(VIDIOC_S_PARM, parm);
    } else {
        DEBUG_LOG(0, "Changing framerate is not supported");
    }
}

void VideoCapture::request_buffers() {
    const int count = 2;

    auto reqbuf = v4l2_requestbuffers{};
    reqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    reqbuf.memory = V4L2_MEMORY_MMAP;
    reqbuf.count = count;

    ioctl(VIDIOC_REQBUFS, reqbuf);

    buffers.clear();
    for (auto i = 0; i < reqbuf.count; i++) {
        auto buffer = std::make_shared<Buffer>(std::ref(*this), i);
        buffer->map();
        buffer->enqueue();
        buffers.push_back(buffer);
    }
}

void VideoCapture::start() {
    request_buffers();

    auto type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    ioctl(VIDIOC_STREAMON, type);
}

Buffer & VideoCapture::dequeue() {
    auto buf = v4l2_buffer{};
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;

    ioctl(VIDIOC_DQBUF, buf);

    return *buffers.at(buf.index);
}

Eigen::MapRMatb * VideoCapture::grab() {
    static auto eg = std::unique_ptr<EnqueueGuard>{};
    eg.reset(new EnqueueGuard{dequeue()});

    Debug::Scope scope = m_debug.sub("Controller");

    for (auto controller : controllers) {
        scope(controller.second->get_name()) =
            controller.second->get_value_raw();
    }

    return decoder->decode(
        static_cast<const unsigned char *>(eg->get_buffer().get_start()),
        eg->get_buffer().get_size());
}

VideoCapture::PixelFormatList VideoCapture::enumerate_pixel_formats() {
    using Pair = PixelFormatList::value_type;

    PixelFormatList result;
    for (int i = 0; i < 16; i++) {
        auto desc = v4l2_fmtdesc{};
        desc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        desc.index = i;
        if (!ioctl(VIDIOC_ENUM_FMT, desc, true)) {
            break;
        }

        auto fourcc =
            std::string{reinterpret_cast<char *>(&desc.pixelformat), 4};
        auto name = std::string{reinterpret_cast<char *>(&desc.description)};
        result.push_back(Pair{fourcc, name});
    }

    return result;
}

void VideoCapture::initialize_controllers() {
    controllers.clear();

    for (auto cid :
         {V4L2_CID_BRIGHTNESS, V4L2_CID_CONTRAST, V4L2_CID_SATURATION,
          V4L2_CID_HUE, V4L2_CID_SHARPNESS, V4L2_CID_GAIN, V4L2_CID_AUTOGAIN,
          V4L2_CID_AUTO_WHITE_BALANCE, V4L2_CID_WHITE_BALANCE_TEMPERATURE,
          V4L2_CID_FOCUS_ABSOLUTE, V4L2_CID_FOCUS_RELATIVE, V4L2_CID_FOCUS_AUTO,
          V4L2_CID_EXPOSURE_AUTO, V4L2_CID_EXPOSURE_ABSOLUTE,
          V4L2_CID_EXPOSURE_AUTO_PRIORITY}) {
        controllers[cid] = std::make_shared<Controller>();
    }

    auto info = v4l2_queryctrl{};
    for (int i = 0; i < 16; ++i) {
        info.id |= V4L2_CTRL_FLAG_NEXT_CTRL;
        if (!ioctl(VIDIOC_QUERYCTRL, info, true)) {
            break;
        }

        auto ctrl = std::make_shared<RealController>(std::ref(*this), info);

        controllers[info.id] = ctrl;

        DEBUG_LOG(IMPORTANT, "Controller" << ctrl->get_name() << "gefunden");
    }
}

Controller & VideoCapture::get_controller(const std::string & name) {
    for (auto & controller : controllers) {
        if (controller.second->get_name() == name) {
            return *controller.second;
        }
    }

    throw std::runtime_error("No such controller");
}


