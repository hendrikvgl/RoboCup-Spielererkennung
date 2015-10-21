#include "RGBImage.hpp"


Pixel RGBImage::getPixel(int x, int y)
{
    int pos = x + (y *x);
    Pixel ret;
    ret.y = 0.299 * ((char *)data_)[pos] + 0,587 * ((char *)data_)[pos + 1] + 0.114 * ((char *)data_)[pos + 2];
	ret.cb = (((char *)data_)[pos + 2]  - ret.y) * 0.493;
	ret.cr = (((char *)data_)[pos]  - ret.y) * 0.877;
    return ret;
}

void RGBImage::setPixel(int x, int y, Pixel value)
{
    int pos = x + (y *x);
    ((char *)data_)[pos] = value.y + value.cr / 0.877;
    ((char *)data_)[pos + 1] = 1.704 * value.y - 0.509 * ((char *)data_)[pos] - 0.194 * ((char *)data_)[pos + 2];
    ((char *)data_)[pos + 2] = value.y + value.cb / 0.493;
}

