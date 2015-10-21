// Image.hpp
// Version: 0.0.2
// Date: 05.02.2015/05.02.2015/13.02.2015
// Author: Oliver Sengpiel

#ifndef IMAGE_HPP
#define IMAGE_HPP

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/videodev2.h>
#include <assert.h>

#include <exception>
#include <string>

#include "ImageTypes.hpp"

//! This is the general exception for ioctl errors occuring in the Capture.
/**
 * If this exception occurs, there is something wrong with the camera. It is
 * either not ready to use or not available in another way.
 **/
class CaptureException : public std::exception
{
public:
    CaptureException(std::string message)
	:message_(message) {}
    ~CaptureException() {}
    virtual const char * what() const noexcept { return message_.c_str(); }
private:
    std::string message_;
};

class Image
{
public:
    Image();
    Image(int fd, v4l2_buffer buf, void * data, int width, 
	    int height);
    virtual ~Image();

    Image(const Image &) = delete;
    Image(Image &&) = delete;

    Image& operator=(const Image &) = delete;
    Image& operator=(Image &&) = delete;
    
    virtual YUYV& getPixel(int x, int y) = 0;

    int getWidth() const { return width_; }
    int getHeight() const { return height_; }

    bool isValid() const { return !(width_ == 0 || height_ == 0); }

    typedef YUYV* iterator;

    iterator begin() { return &getPixel(0,0); }
    iterator end() { return &getPixel(width_-1,height_-1); }

    // These methods are for the raw access on the data. I would disadvice you
    // from using this methods, because it does not ensure your data to be
    // valid. Please use this methods only if you know what you are doing.  If
    // you plan to use this feature define CAPTURE_RAW_IMAGE_ACCESS at the
    // beginning of your project.

    void * getData() const { return data_; }

protected:
    void * data_ = nullptr;
    int fd_ = 0;
    v4l2_buffer buf_ = v4l2_buffer();

    int width_ = 0;
    int height_ = 0;
};

class NoImage : public Image
{
public:
    NoImage() = default;
    ~NoImage() = default;

    YUYV& getPixel(int, int) override { return (dummy_ = YUYV()); }
private:
    YUYV dummy_;
};

#endif
