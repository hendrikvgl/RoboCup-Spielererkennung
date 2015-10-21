// Capture.hpp
// Version: 0.2.1
// Date: 05.02.2015/10.02.2015/13.02.2015
// Author: Oliver Sengpiel

#ifndef CAPTURE_HPP
#define CAPTURE_HPP

#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/videodev2.h>
#include <unistd.h>
#include <cassert>

#include <string>
#include <vector>
#include <exception>
#include <memory>

#include "Buffer.hpp"
#include "Controller.hpp"

#include "Image.hpp"
#include "YUYVImage.hpp"


//! This exception is thrown, when none of the buffers provides an image.
/**
 * This exception can be ignored in all cases. It only exists to indicate, that
 * there was no new image in the buffers. It requires no special treatment.
 **/
class NoFrameException : public std::exception
{
public:
    NoFrameException() {}
    ~NoFrameException() {}
};

//! A wrapper struct for the fourcc
/**
 * This is a wrapper that ensures that the string given to the capture is
 * exactly 4 characters wide.
 */
struct Fourcc
{
    std::string fourcc;
    explicit Fourcc(std::string && format)
    {
	assert(format.size() == 4);
	fourcc = std::forward<std::string>(format);
    }
};

//! This is a wrapper class for the video device path
/**
 * This wrapper ensures that the opened file is really a /dev/video* file.
 */
class VideoDeviceFile
{
public:
    explicit VideoDeviceFile(int number) :
	path_(std::string("/dev/video") + std::to_string(number)) 
    {
	assert(number >= 0);
    }
    const char * getPath() { return path_.c_str(); }

private:
    std::string path_;
};


//! The class which handles the communication with the camera.
/**
 * This is the interface with the hardware camera. The device (like
 * /dev/video0) is accessed and initialized with only calling the constructor
 * of this class. The width and heigt of the picture provided by the webcam are
 * stated here, as well as the fps (which is 25 by default) and the count of
 * the buffers (which is standard 3).
 *
 * The format of the picture has to be a string containing four characters
 * (e.g. "YUYV"). The format given to the constructor determines which format
 * the camera writes to the buffer.
 **/
class Capture
{
public:
    Capture(VideoDeviceFile device, int width, int height , const
	    Fourcc fourcc, int bufferNr = 3);
    ~Capture();

    std::unique_ptr<Image> getFrame();
    Controller getController();
private:
    int fd_;
    std::vector<Buffer> buffer_;
    int width_, height_;
};

#endif
