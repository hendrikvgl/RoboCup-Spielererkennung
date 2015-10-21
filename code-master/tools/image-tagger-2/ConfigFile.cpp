#include "ConfigFile.hpp"

Change imageToChange(sf::Image & img)
{
    Change tmpChange;

    for (int y = 0; y < img.getSize().y; ++y)
    {
        for (int x = 0; x < img.getSize().x; ++x)
        {
            if (img.getPixel(x, y) != sf::Color(0, 0, 0))
            {
                tmpChange.pixel.emplace_back(std::make_pair(x, y));
            }
        }
    }

    return tmpChange;
};

bool ConfigFile::isInConfig(int y, int cb, int cr)
{
    bool first = (configImage_.getPixel(cb, y) != sf::Color(0, 0, 0));
    bool second = (configImage_.getPixel(cr + 256, y) != sf::Color(0, 0, 0));
    bool third = (configImage_.getPixel(cr + 512, cb) != sf::Color(0, 0, 0));

    return first && second && third;
}

void ConfigFile::loadImage(std::string s)
{
    if (configImage_.loadFromFile(s))
    {
        std::cout << "Loading successful." << std::endl;
    }
    else
    {
        configImage_.create(256 * 3, 256, sf::Color(0, 0, 0));
        std::cout << "Creating new image." << std::endl;
    }
}

void ConfigFile::draw(sf::RenderWindow & window)
{
    sf::Sprite sprite;
    texture_.loadFromImage(configImage_);
    sprite.setTexture(texture_);

    sprite.setPosition(0, 544);

    window.draw(sprite);
}

ConfigFile::ConfigFile(std::string path) : path_(path)
{
    loadImage(path_ + ".png");
    history_.emplace_front(imageToChange(configImage_));
}

using namespace boost::gil;

void ConfigFile::save()
{
    std::cout << "Saving..." << std::endl;

    gray8_image_t image(3 * 256, 256);
    gray8_pixel_t black(0);
    gray8_pixel_t white(255);

    auto imageview = view(image);

    fill_pixels(imageview, black);

    for(int y = 0; y < configImage_.getSize().y; ++y)
    {
	for(int x = 0; x < configImage_.getSize().x; ++x)
        {
            if (configImage_.getPixel(x, y) != sf::Color::Black)
            {
		imageview(x,y) = white;
            }
        }
    }
    png_write_view(path_ + ".png", imageview);
}

void ConfigFile::add(Change change)
{
    Change result;
    for (auto p : change.pixel)
    {
        if (configImage_.getPixel(p.first, p.second) == sf::Color(0, 0, 0))
        {
            configImage_.setPixel(p.first, p.second, sf::Color(255, 255, 255));
            result.pixel.push_back(p);
        }
    }
    history_.push_front(result);
    undone_.clear();
}

void ConfigFile::remove(Change change)
{
    Change result;
    for (auto p : change.pixel)
    {
        if (configImage_.getPixel(p.first, p.second) != sf::Color(0, 0, 0))
        {
            configImage_.setPixel(p.first, p.second, sf::Color(0, 0, 0));
            result.pixel.push_back(p);
        }
    }
    history_.push_front(result);
    undone_.clear();
}

void ConfigFile::undo()
{
    if (history_.empty())
    {
        std::cout << "Nothing to undo!" << std::endl;
    }
    else
    {
        undone_.push_front(history_.front());
        history_.pop_front();
        for (auto p : undone_.front().pixel)
        {
            auto pixel = configImage_.getPixel(p.first,p.second);
            configImage_.setPixel(p.first, p.second, sf::Color(sf::Color::White.r - pixel.r, sf::Color::White.g - pixel.g, sf::Color::White.b - pixel.b));
        }
    }
}

void ConfigFile::redo()
{
    if (undone_.empty())
    {
        std::cout << "Nothing to redo!" << std::endl;
    }
    else
    {
        history_.push_front(undone_.front());
        undone_.pop_front();
        for (auto p : history_.front().pixel)
        {
            auto pixel = configImage_.getPixel(p.first,p.second);
            configImage_.setPixel(p.first, p.second, sf::Color(sf::Color::White.r - pixel.r, sf::Color::White.g - pixel.g, sf::Color::White.b - pixel.b));
        }
    }
}
