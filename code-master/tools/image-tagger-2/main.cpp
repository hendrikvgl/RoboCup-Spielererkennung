#include <iostream>
#include <list>
#include <vector>

#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <SFML/System.hpp>

#include <yaml-cpp/yaml.h>

#include "Capture/Capture.hpp"
#include "ConfigFile.hpp"

#ifndef PROJECT_DIR
    #define PROJECT_DIR /home/darwin/darwin
#endif
#ifndef INSTALL_DIR
    #define INSTALL_DIR /home/darwin/darwin
#endif
#define INDIRECTION(A,B) B(A)
#define STR(X) #X
static const std::string project_root=std::string(INDIRECTION(PROJECT_DIR, STR));
static const std::string install_root=std::string(INDIRECTION(INSTALL_DIR, STR));
static const std::string relative_config_path = "/share/bitbots/config/image-tagger.yaml";
static const std::string default_config_file=project_root + relative_config_path;
static const std::string default_installed_config_file=install_root + relative_config_path;
#undef PROJECT_DIR
#undef PROJECT_DIR
#undef INDIRECTION
#undef STR

static bool use_installed_config = true;

struct RGBA
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
};

template<typename Clazz, typename... T>
inline void secure_call(void(Clazz::* func)(T...), Clazz& c, T... t) {
    try {
        std::bind(func,c,t...)();
    } catch(const ControllerException& exp) {
        std::cerr<<exp.what()<<std::endl; \
    }
}

template<typename T>
T get_conf_value(const YAML::Node& config, const std::string& key,const T& default_value);

template<>
std::string get_conf_value<std::string>(const YAML::Node& config, const std::string& key,const std::string& default_value) {
    try {
        return config[key].as<std::string>();
    } catch (const std::runtime_error& err) {
        std::cerr<<"Failed to read config: "<<key<<": "<<err.what()<<std::endl;
        return default_value;
    }
}
template<typename T>
T get_conf_value(const YAML::Node& config, const std::string& key,const T& default_value) {
    try {
        return config[key].as<T>();
    } catch (const std::runtime_error& err) {
        std::cerr<<"Failed to read config: "<<key<<": "<<
            get_conf_value<std::string>(config, key, "")<<"\nException: "<<err.what()<<std::endl;
        return default_value;
    }
}

int main(int argc, char ** argv)
{
    std::string output_path = "";
    if (argc > 1)
        output_path = std::string(argv[1]);
    else
        output_path = std::string("configfile");

    ConfigFile config(output_path);

    sf::RenderWindow window(sf::VideoMode(3 * 256, 544 + 256), "Configurator");
    sf::RectangleShape rectshape;
    sf::View view(sf::Vector2f(3 * 128, (544 + 256) / 2),
                  sf::Vector2f(3 * 256, 544 + 256));
    window.setView(view);

    Capture capture(VideoDeviceFile(0), 960, 544, Fourcc("YUYV"));

    {
        auto controller = capture.getController();

        YAML::Node yaml_cofig;
        if(use_installed_config)
            yaml_cofig = YAML::LoadFile(default_installed_config_file.data());
        else
            yaml_cofig = YAML::LoadFile(default_config_file.data());

        bool autoWhiteBalanceOn = get_conf_value(yaml_cofig, "AutoWhiteBalanceOn", false);
        int whiteBalanceTemperature = get_conf_value(yaml_cofig, "WhiteBalanceTemperature", 255 / 2);
        int brigthness = get_conf_value(yaml_cofig, "Brigthness", 255 / 2);
        bool focusAuto = get_conf_value(yaml_cofig, "FocusAuto", false);
        int focusAbsolute = get_conf_value(yaml_cofig, "FocusAbsolute", 10);
        int gain = get_conf_value(yaml_cofig, "Gain", 32);
        bool exposureAuto = get_conf_value(yaml_cofig, "ExposureAuto", true);
        bool exposureAutoPriority = get_conf_value(yaml_cofig, "ExposureAuto", false);
        int contrast = get_conf_value(yaml_cofig, "Contrast", 255 * 14 / 100);

        secure_call(&Controller::toggleAutoWhiteBalanceOn, controller, autoWhiteBalanceOn);
        secure_call(&Controller::setWhiteBalanceTemperature, controller, whiteBalanceTemperature);
        secure_call(&Controller::setBrigthness, controller, brigthness);
        secure_call(&Controller::toggleFocusAuto, controller, focusAuto);
        secure_call(&Controller::setFocusAbsolute, controller, focusAbsolute);
        secure_call(&Controller::setGain, controller, gain);
        secure_call(&Controller::toggleExposureAuto, controller, exposureAuto);
        secure_call(&Controller::toggleExposureAutoPriority, controller, exposureAutoPriority);
        secure_call(&Controller::setContrast, controller, contrast);
    }

    rectshape.setFillColor(sf::Color(0, 0, 0, 0));
    rectshape.setOutlineThickness(1.f);
    rectshape.setOutlineColor(sf::Color(255, 100, 100));

    sf::Image current_image;
    current_image.create(960 / 2, 544, sf::Color(255, 255, 255));

    sf::Texture cameratex;
    cameratex.loadFromImage(current_image);
    sf::Sprite camerasprite;
    camerasprite.setPosition(0, 0);
    camerasprite.setTexture(cameratex);

    decltype(capture.getFrame()) frame;

    while (window.isOpen())
    {
        if (sf::Keyboard::isKeyPressed(sf::Keyboard::Space))
        {
            auto newframe = capture.getFrame();
            if (newframe && newframe->isValid())
            {
                frame.swap(newframe);
            }
        }

        if (frame && frame->isValid())
        {
            for (int y = 0; y < frame->getHeight(); ++y)
            {
                for (int x = 0; x < frame->getWidth(); ++x)
                {
                    YUYV & pixel = frame->getPixel(x, y);
                    if (!config.isInConfig(pixel.left.y, pixel.left.cb,
                                           pixel.left.cr))
                    {
                        current_image.setPixel(x, y, sf::Color(pixel.left.y,
                                                               pixel.left.y,
                                                               pixel.left.y));
                    }
                    else
                    {
                        current_image.setPixel(x, y, sf::Color(0, 255, 0));
                    }
                }
            }
            cameratex.loadFromImage(current_image);
            camerasprite.setTexture(cameratex);
        }

        window.clear(sf::Color(100, 100, 100));

        window.draw(camerasprite);
        window.draw(rectshape);
        config.draw(window);

        window.display();

        sf::Event event;

        while (window.pollEvent(event))
        {
            if (event.type == sf::Event::MouseButtonPressed)
            {
                auto relative = sf::Mouse::getPosition() - window.getPosition();
                if (relative.x < 0)
                    relative.x = 0;
                if (relative.y < 0)
                    relative.y = 0;
                if (relative.x > 960 / 2)
                    relative.y = 960 / 2;
                if (relative.y > 544)
                    relative.y = 544;

                rectshape.setPosition(relative.x, relative.y);
                rectshape.setOutlineThickness(0.f);
            }
            else if (event.type == sf::Event::MouseButtonReleased)
            {
                auto relative = sf::Mouse::getPosition() - window.getPosition();
                if (relative.x < 0)
                    relative.x = 0;
                if (relative.y < 0)
                    relative.y = 0;
                if (relative.x > 960 / 2)
                    relative.x = 960 / 2;
                if (relative.y > 544)
                    relative.y = 544;

                rectshape.setSize(
                    sf::Vector2f(relative.x - rectshape.getPosition().x,
                                 relative.y - rectshape.getPosition().y));
                rectshape.setOutlineThickness(1.f);
            }
            else if (event.type == sf::Event::KeyPressed)
            {
                if (frame && frame->isValid())
                {
                    if (event.key.code == sf::Keyboard::A)
                    {
                        Change change;
                        for (int y = rectshape.getPosition().y;
                             y < rectshape.getSize().y +
                                     rectshape.getPosition().y;
                             ++y)
                        {
                            for (int x = rectshape.getPosition().x;
                                 x < rectshape.getSize().x +
                                         rectshape.getPosition().x;
                                 ++x)
                            {
                                auto pixel = frame->getPixel(x, y).left;

                                change.pixel.push_back(
                                    std::make_pair(static_cast<int>(pixel.cb),
                                                   static_cast<int>(pixel.y)));
                                change.pixel.push_back(std::make_pair(
                                    static_cast<int>(pixel.cr) + 256,
                                    static_cast<int>(pixel.y)));
                                change.pixel.push_back(std::make_pair(
                                    static_cast<int>(pixel.cr) + 512,
                                    static_cast<int>(pixel.cb)));
                            }
                        }
                        config.add(change);
                    }
                    else if (event.key.code == sf::Keyboard::Z &&
                             event.key.control)
                    {
                        config.undo();
                    }
                    else if (event.key.code == sf::Keyboard::U &&
                             event.key.control)
                    {
                        config.redo();
                    }
                    else if (event.key.code == sf::Keyboard::S &&
                             event.key.control)
                    {
                        config.save();
                    }
                    else if (event.key.code == sf::Keyboard::R)
                    {
                        Change change;
                        for (int y = rectshape.getPosition().y;
                             y < rectshape.getSize().y +
                                     rectshape.getPosition().y;
                             ++y)
                        {
                            for (int x = rectshape.getPosition().x;
                                 x < rectshape.getSize().x +
                                         rectshape.getPosition().x;
                                 ++x)
                            {
                                auto pixel = frame->getPixel(x, y).left;

                                change.pixel.push_back(
                                    std::make_pair(static_cast<int>(pixel.cb),
                                                   static_cast<int>(pixel.y)));
                                change.pixel.push_back(std::make_pair(
                                    static_cast<int>(pixel.cr) + 256,
                                    static_cast<int>(pixel.y)));
                                change.pixel.push_back(std::make_pair(
                                    static_cast<int>(pixel.cr) + 512,
                                    static_cast<int>(pixel.cb)));
                            }
                        }
                        config.remove(change);
                    }
                }
            }
            else if (event.type == sf::Event::Closed)
            {
                window.close();
            }
            else if (event.key.code == sf::Keyboard::Escape)
            {
                window.close();
            }
            else
            {
            }
        }
    }
}
