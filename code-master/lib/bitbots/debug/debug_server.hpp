#ifndef _DEBUG_SERVER_HPP
#define _DEBUG_SERVER_HPP

#include "debug_intern.hpp"
#include "debug_serialize.hpp"
#include "debug_type_info.hpp"

#include <sstream>
#include <iostream>

#include <Eigen/Core>

#include <boost/utility.hpp>


namespace Debug {
namespace server {

class Context : boost::noncopyable {
private:
    std::stringstream stream;
    Serialize::InputArchive archive;

    std::string name;
    uint8_t type;

public:
    Context(const std::string& data)
        : stream(data), archive(stream) {

        archive & name;
        archive & type;
    }

    const std::string& get_name() const {
        return name;
    }

    uint8_t get_type() const {
        return type;
    }

    template<class T>
    void get_object(T& obj) {
        archive & obj;
    }
};

inline
std::shared_ptr<Context> make_context(const char *data, int n) {
    return std::shared_ptr<Context>(new Context(std::string(data, n)));
}

// namespace
}}

#endif

