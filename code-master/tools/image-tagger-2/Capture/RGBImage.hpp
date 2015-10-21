// RGBImage.hpp
// Version: 0.0.2
// Date: 06.02.2015/06.02.2015/13.02.2015
// Author: Dennis Reher, Oliver Sengpiel

#ifndef RGBIMAGE_HPP
#define RGBIMAGE_HPP

#include "Image.hpp"

class RGBImage : public Image
{
public:
    using Image::Image;

    Pixel getPixel(int x, int y) override;
    void  setPixel(int x, int y, Pixel value) override;
};

#endif

