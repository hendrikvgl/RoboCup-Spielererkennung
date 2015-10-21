#include "Image.hpp"

Image::Image() = default;
Image::Image(int fd, v4l2_buffer buf, void * data, int width, int height)
    : data_(data), fd_(fd), buf_(buf), width_(width), height_(height)
{
    assert(fd > 0);
    assert(data != nullptr);
}
Image::~Image()
{
    if(data_)
    {
	if(ioctl(fd_, VIDIOC_QBUF, &buf_) == -1)
	    throw CaptureException("Enqueueing buffer failed (getFrame).");
    }
}
