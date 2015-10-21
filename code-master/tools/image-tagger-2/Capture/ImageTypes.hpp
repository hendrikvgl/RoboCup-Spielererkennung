#ifndef IMAGETYPES_HPP
#define IMAGETYPES_HPP

union YUYV
{
    struct YUYVl
    {
        uint8_t y;
        uint8_t cb;
        unsigned : 8;
        uint8_t cr;
    } left;
    struct YUYVr
    {
        unsigned : 8;
        uint8_t cb;
        uint8_t y;
        uint8_t cr;
    } right;
};

struct YUV
{
    uint8_t y;
    uint8_t cb;
    uint8_t cr;
};
#endif
