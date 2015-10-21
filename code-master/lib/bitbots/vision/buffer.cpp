#include "buffer.hpp"
#include "capture.hpp"

#include <sys/mman.h>
#include <cstdlib>
#include <cerrno>

using namespace Vision::Video;

Buffer::Buffer(VideoCapture & capture, int idx)
    : capture(capture), buffer(v4l2_buffer{}),
      start(MAP_FAILED) {

    buffer.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buffer.memory = V4L2_MEMORY_MMAP;
    buffer.index = idx;
}

Buffer::~Buffer() {
    if (start != MAP_FAILED) {
        ::munmap(start, buffer.length);
    }
}

void Buffer::map() {
    capture.ioctl(VIDIOC_QUERYBUF, buffer);
    start = ::mmap(NULL, buffer.length, PROT_READ | PROT_WRITE, MAP_SHARED,
                   capture.get_fd(), buffer.m.offset);

    if (start == MAP_FAILED) {
        throw VideoError("querybuf failed");
    }
}

void Buffer::enqueue() { capture.ioctl(VIDIOC_QBUF, buffer); }

EnqueueGuard::EnqueueGuard(Buffer & buffer) : buffer(buffer) {}

EnqueueGuard::~EnqueueGuard() { buffer.enqueue(); }

Buffer & EnqueueGuard::get_buffer() { return buffer; }
