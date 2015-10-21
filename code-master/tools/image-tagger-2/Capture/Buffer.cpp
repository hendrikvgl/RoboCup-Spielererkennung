#include "Buffer.hpp"

Buffer::Buffer() { }

Buffer::Buffer(void * data, int width, int height, size_t size)
    :data_(data), width_(width), height_(height), size_(size)
{

}

Buffer::~Buffer()
{

}

void * Buffer::getData() const
{
    return data_;
}

int Buffer::getWidth() const
{
    return width_;
}

int Buffer::getHeight() const
{
    return height_;
}

size_t Buffer::getSize() const
{
    return size_;
}
