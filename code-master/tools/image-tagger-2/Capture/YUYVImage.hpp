// YUYVImage.hpp
// Version: 0.0.3
// Date: 05.02.2015/05.02.2015/13.02.2015
// Author: Oliver Sengpiel, Dennis Reher

#ifndef YUYVIMAGE_HPP
#define YUYVIMAGE_HPP

#include "Image.hpp"

class YUYVImage : public Image
{
public:
    using Image::Image;

    YUYV& getPixel(int x, int y) override;
};

#endif
