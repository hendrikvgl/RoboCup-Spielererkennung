#ifndef _NOOP_IMAGE_DECODER_HPP
#define _NOOP_IMAGE_DECODER_HPP

#include <iostream>
#include <Eigen/Core>

#include "image_decoder.hpp"

namespace Vision {
namespace Video {
namespace Decoder {

/**
 * \brief The image decoder to enable access on a given image.
 *
 * This noop implementation just stores a pointer and has no more functionality
 * Once there were more decoders, but they weren't used, so we abandoned them
 */
class NoopImageDecoder : public ImageDecoder {
public:
    NoopImageDecoder(int width, int height)
        : ImageDecoder(width, height) {
    }

    virtual Eigen::MapRMatb* decode(const unsigned char* raw, int n) {
        int stride = n / height;

        const Eigen::MapRMatb* data = new Eigen::MapRMatb(const_cast<char*>((char*)raw), height, stride);
        return const_cast<Eigen::MapRMatb*>(data);
    }
};

} } } //namespace

#endif

