#ifndef _IMAGE_DECODER_HPP
#define _IMAGE_DECODER_HPP

#include <Eigen/Core>
#include "../util/eigen_util.hpp"

namespace Vision {
namespace Video {
namespace Decoder {

    class ImageDecoder {
    protected:
        const int width, height;

    public:
        ImageDecoder(int width, int height)
            : width(width), height(height) {
        }

        virtual ~ImageDecoder() {};
        virtual Eigen::MapRMatb* decode(const unsigned char*raw, int n) = 0;
    };
} } } //namespace

#endif

