#ifndef BITBOTS_VISION_BUFFER_HPP
#define BITBOTS_VISION_BUFFER_HPP

#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>

#include <linux/videodev2.h>

namespace Vision {
namespace Video {

class VideoCapture;

/**
    Ein VideoBuffer für MemoryMap-IO
*/
class Buffer {
public:
    Buffer(VideoCapture & capture, int idx);
    ~Buffer();

    void map();
    void enqueue();

    inline
    void * get_start() const { return start; }

    inline
    int get_size() const { return buffer.length; }

private:
    VideoCapture & capture;
    v4l2_buffer buffer;

    void * start;
};

/**
    Kleines Objekt, welches bei seiner Zerstörung buffer.enqueue() aufruft.
*/
class EnqueueGuard {
public:
    EnqueueGuard(Buffer & buffer);

    ~EnqueueGuard();

    Buffer & get_buffer();

private:
    Buffer & buffer;
};

}
}
#endif
