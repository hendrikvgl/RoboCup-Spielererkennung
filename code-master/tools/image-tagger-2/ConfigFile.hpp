#ifndef CONFIGFILE_HPP
#define CONFIGFILE_HPP

#include <list>
#include <iostream>

#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <SFML/System.hpp>

// libpng dropped this definition but boost needs it ...
#define int_p_NULL (int*)NULL

#include <boost/gil/gil_all.hpp>
#include <boost/gil/extension/io/png_dynamic_io.hpp>

struct Change
{
    std::vector<std::pair<int, int>> pixel = {};
};

Change imageToChange(sf::Image & img);

class ConfigFile
{
public:
    explicit ConfigFile(std::string path);

    void add(Change change);
    void remove(Change change);

    bool isInConfig(int y, int cb, int cr);

    void undo();
    void redo();

    void save();
    void draw(sf::RenderWindow & window);

    typedef std::vector<std::pair<int, int>>::iterator iterator;

    iterator begin() { return history_.front().pixel.begin(); }
    iterator end() { return history_.front().pixel.end(); }

private:
    std::string path_;
    sf::Image configImage_;
    std::list<Change> history_;
    std::list<Change> undone_;

    sf::Texture texture_;

    void loadImage(std::string s);
};

#endif
