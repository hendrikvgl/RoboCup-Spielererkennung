#ifndef VISION_ADAPTER_HPP__
#define VISION_ADAPTER_HPP__

#include <iostream>
#include <Eigen/Core>
#include <Eigen/LU>
#include "../debug/debug.hpp"
#include "../debug/debugmacro.h"
#include "../util/eigen_util.hpp"

namespace Vision {
namespace Adapter {
namespace pa = Debug::Paint;

/**
 * The abstract Adapter interface for our vision.
 * An adapter is a wrapper for a given image in any of the following data formats: bgr, yuyv i420
 * The adapter assures a save acces on the image, without knowing the raw data format
 */
class AbstractAdapter {
protected:
int width, height;
mutable int count;
public:
    int get_width() const {
        return width;
    }

    int get_height() const {
        return height;
    }

    template<class S>
        S size() const {
        return S(get_width(), get_height());
    }
};

/**
 * The adapter used most often. This adapter enables us to easily access an yuv image from a yuyv
 */
class RawYUYVAdapter: public AbstractAdapter {
private:
Eigen::MapRMatVec4Ub yuyv;

public:

    RawYUYVAdapter()
    : yuyv(nullptr, 0, 0){
    }

    RawYUYVAdapter(const Eigen::MapRMatb& mat)
    : yuyv(const_cast<Eigen::Vector4Ub*>((Eigen::Vector4Ub*)mat.data()), mat.rows(), mat.cols() / 4) {
        width = mat.cols()/2;
        height = mat.rows();
        count = 0;
    }

    ~RawYUYVAdapter() {
        IF_DEBUG_WITH_EXPRESSION(3,STANDART_IF_DEBUG_EXPRESSION(3),Debug::Scope("Vision.DebugImage")("touched") = count);
    }

    Eigen::Vector3i operator()(int x, int y) const {
        if(yuyv.data() == nullptr) return Eigen::Vector3i::Zero();
        ++count;

        const Eigen::Vector4Ub& px(yuyv(y, x/2));

        Eigen::Vector3i result;
        if(x & 1) {
            result << px(2), px(1), px(3);
        } else {
            result << px(0), px(1), px(3);
        }

        return result;
    }

    /* This needs to be here, because C++ inlines this function and does not bind it dynamicly like java */
    template<class P>
        Eigen::Vector3i operator()(const P& point) const {
        return (*this)((int)point(0), (int)point(1));
    }
};

//The Conversion Matrix found at Wikipedia
#if 0
Eigen::Matrix3f rgb_to_yuv_conversion = (Eigen::Matrix3f() << 0.299,    0.587,    0.114,
                                                              -0.14713, -0.28886, 0.43616,
                                                               0.61509,  -0.51499, -0.10001).finished();
#else
static const Eigen::Matrix3f rgb_to_yuv_conversion = (Eigen::Matrix3f() << 0.2126,    0.7152,    0.0722,
                                                             -0.09991, -0.33609, 0.43616,
                                                              0.615,  -0.55861, -0.05639).finished();
//                                                            0.615,  -0.51499, -0.10001).finished();
#endif
static const Eigen::Matrix3f yuv_to_rgb_conversion = rgb_to_yuv_conversion.inverse();

static const float umax = 0.43616;
static const float vmax = 0.61509;
static const float uconversion = 1.0 / umax / 2.0;
static const float vconversion = 1.0 / vmax / 2.0;

inline
Eigen::Vector3i RGBtoYUV(unsigned int r, unsigned int g, unsigned int b)
{
    /*Calculate the basic rgb yuv conversion*/ 
    Eigen::Vector3f result = (rgb_to_yuv_conversion * Eigen::Vector3f(r,g,b)); 
    /* scale the u and v channel, The Matrix transformation returns v in
     * [0,255], u in [-umax, umax], v in [-vmax, vmax]
     */ 
    result(1) *= uconversion; 
    result(2) *= vconversion; 
    /*shift the u and v channel to the "zero"*/ 
    result += Eigen::Vector3f(0,128,128); 
    
    return result.cast<int>(); 
}

/**
 * A simple bgr to yuv adapter. Points will be converted to yuv on access.
 */
class BGRYUVAdapter: public AbstractAdapter {
protected:
Eigen::MapRMatVec3Ub bgr;

public:

    BGRYUVAdapter()
    :bgr(nullptr, 0, 0){
    }

    BGRYUVAdapter(const Eigen::MapRMatb& mat)
    : bgr(const_cast<Eigen::Vector3Ub*>((const Eigen::Vector3Ub*)mat.data()), mat.rows(), mat.cols() / 3) {
        width = bgr.cols();
        height = bgr.rows();
        count = 0;
    }

    ~BGRYUVAdapter() {
        Debug::Scope("Vision.DebugImage")("touched") = count;
    }

    Eigen::Vector3i operator()(int x, int y) const { 
        ++count; 
        Eigen::Vector3Ub bgr_px(bgr(y, x)); 
        return RGBtoYUV(bgr_px(2), bgr_px(1), bgr_px(0)); 
    }

    /* This needs to be here, because C++ inlines this function and does not bind it dynamicly like java */
    template<class P>
        Eigen::Vector3i operator()(const P& point) const {
        return (*this)((int)point(0), (int)point(1));
    }
};

class RGBYUVAdapter : public BGRYUVAdapter {
public:
    RGBYUVAdapter(const Eigen::MapRMatb& mat)
    :BGRYUVAdapter(mat)
    {}

    Eigen::Vector3i operator()(int x, int y) const { 
        ++count; 
        Eigen::Vector3Ub bgr_px(bgr(y, x)); 
        return RGBtoYUV(bgr_px(0), bgr_px(1), bgr_px(2)); 
    }

    /* This needs to be here, because C++ inlines this function and does not bind it dynamicly like java */
    template<class P>
    Eigen::Vector3i operator()(const P& point) const {
        return (*this)((int)point(0), (int)point(1));
    }
};

/**
 * This adapter is the result of our wish to use the I420 image format. Unfortunately our camera doesn't support this on linux.
 */
class IYUVAdapter : public AbstractAdapter {
private:
    Eigen::MapRMatUb m_y, m_u, m_v;
    typedef unsigned char uchar;
public:
    IYUVAdapter(const Eigen::MapRMatb& mat)
    :m_y(const_cast<uchar*>((uchar*)mat.data()), mat.rows(), mat.cols() * 2 / 3),
    m_u(const_cast<uchar*>((uchar*)mat.data() + mat.rows() * mat.cols() * 2 / 3), mat.rows() / 2, mat.cols() / 3),
    m_v(const_cast<uchar*>((uchar*)mat.data() + mat.rows() * mat.cols() * 5 / 6), mat.rows() / 2, mat.cols() / 3) {
        //reshape the matrix to contain just one byte per vector
        width = mat.cols() *2 / 3;
        height = mat.rows();
        count = 0;
        L_DEBUG(std::cout<<"IYUVAdapter: width"<<width<<" height: "<<height<<std::endl);
    }

    ~IYUVAdapter() {
        Debug::Scope("Vision.DebugImage")("touched") = count;
    }

    Eigen::Vector3i operator()(int x, int y) const {
        ++count;
        return Eigen::Vector3i(m_y(y,x),m_u(y/2,x/2),m_v(y/2,x/2));
    }

    /* This needs to be here, because C++ inlines this function and does not bind it dynamicly like java */
    template<class P>
    Eigen::Vector3i operator()(const P& point) const {
        return (*this)((int)point(0), (int)point(1));
    }
};

/**
 * A simple Adapter for inverted pictures, like pictures from the original darwin webcams
 * Currently we use normal adjusted cameras
 */
template<class Base>
class InvertedPictureAdapter: public AbstractAdapter{
private:
Base base;

public:
    InvertedPictureAdapter(const Eigen::MapRMatb& mat)
    :base(mat) {
        width = base.get_width();
        height = base.get_height();
    }

    Eigen::Vector3i operator()(int x, int y) const {
        return base(width - x - 1, height - y - 1);
    }

    /* This needs to be here, because C++ inlines this function and does not bind it dynamicly like java */
    template<class P>
    Eigen::Vector3i operator()(const P& point) const {
        return (*this)((int)point(0), (int)point(1));
    }
};

} }//namespace

#endif
