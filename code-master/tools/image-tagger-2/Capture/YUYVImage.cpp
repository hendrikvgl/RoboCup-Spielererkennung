#include "YUYVImage.hpp"

/**
 * An YUYV image consists of pairs, which share the same color values and differ
 * only in the brightness value of the pixels. So the memory of one pair of
 * pixels is mapped to the memory as
 *
 *  0    1    2    3
 * | Y1 | Cb | Y2 | Cr |
 *
 * where one cell is exactly one byte.
 *
 * The result of this are the different positions of the color values which are
 * calculated in the extractYUYVData(unsigned int,unsigned int) function.
 **/
YUYV& YUYVImage::getPixel(int x, int y)
{
    return ((YUYV *)data_)[x/2 + y*getWidth()/2];
}
