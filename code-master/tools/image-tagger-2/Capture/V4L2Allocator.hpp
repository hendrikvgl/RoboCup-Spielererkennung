#ifndef V4L2ALLOCATOR_HPP
#define V4L2ALLOCATOR_HPP

#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/videodev2.h>
#include <unistd.h>
#include <cassert>

#include <algorithm>

class V4L2Allocator
{
public:
    static void requestBuffers( int fd, int number )
    {
        assert( fd > 0 );
        assert( number > 0 );

	fd_ = fd;

        // Request buffers
        v4l2_requestbuffers request = v4l2_requestbuffers();

        request.count = number;
        request.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        request.memory = V4L2_MEMORY_MMAP;

        if ( ioctl( fd_, VIDIOC_REQBUFS, &request ) == -1 )
            throw CaptureException( "Buffer request failed." );

        // Create the image buffer
        for ( unsigned int i = 0; i < request.count; i++ )
        {
            v4l2_buffer buf = v4l2_buffer();
            buf.index = i;
            buf.type = request.type;
            buf.memory = request.memory;

            if ( ioctl( fd_, VIDIOC_QUERYBUF, &buf ) == -1 )
                throw CaptureException( "Buffer query failed." );

            auto start = mmap( NULL, buf.length, PROT_READ | PROT_WRITE,
                               MAP_SHARED, fd_, buf.m.offset );
            if ( start == MAP_FAILED )
                throw CaptureException( "MMAP failed." );

            buffer_.emplace_back( start, width_, height_, buf.length );
        }

        for ( unsigned int i = 0; i < buffer_.size(); i++ )
        {
            v4l2_buffer buf = v4l2_buffer();
            buf.index = i;
            buf.type = request.type;
            buf.memory = request.memory;

            if ( ioctl( fd_, VIDIOC_QBUF, &buf ) == -1 )
                throw CaptureException(
                    "Enqueueing buffer failed (constructor)." );
        }
    }

    static void * allocate()
    {
        // Get a frame
        v4l2_buffer buf = v4l2_buffer();
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;

        if ( ioctl( fd_, VIDIOC_DQBUF, &buf ) == -1 )
            return nullptr;

        return buffer_[buf.index].getData();
    }

    static void * deallocate(void * ptr,size_t)
    {
        for ( int i = 0; i < buffer_.size(); ++i )
        {
            if ( buffer_[i].getData() == ptr )
            {
                v4l2_buffer buf = v4l2_buffer();
                buf.index = i;
                buf.type = request.type;
                buf.memory = request.memory;

                if ( ioctl( fd_, VIDIOC_QBUF, &buf_ ) == -1 )
                    throw CaptureException(
                        "Enqueueing buffer failed (getFrame)." );
            }
        }
    }

private:
    static int fd_;
    static std::vector<Buffer> buffer_;
};

#endif 
