#ifndef _DEBUG_HPP
#define _DEBUG_HPP

#include "debug_type_info.hpp"
#include "debug_intern.hpp"

#include <boost/date_time/posix_time/posix_time_types.hpp>

namespace Debug {
/**
 * Ein Scope, unter dessen Namen alle von ihm initiierten Debug
 * Objekte gestellt werden.
 */
class Scope {
public:
    explicit Scope(const std::string& name, bool console_out = true)
        : name(name), console_out(console_out) {

        enabled = (getenv("DEBUG") != nullptr);
    }

    Scope(const Scope& parent, const std::string& name, bool console_out = true)
        : name(parent.name + "." + name), console_out(console_out) {

        enabled = (getenv("DEBUG") != nullptr);
    }

    Scope sub(const std::string& name, bool console_out = true) {
        return Scope(*this, name, console_out);
    }

    template<class T>
    intern::LogStringStream::Wrapper operator<<(const T& val) {
        return intern::LogStringStream::Wrapper(name + ".log", enabled, DebugType::LOG, console_out) << val;
    }

    intern::ObjectForward operator()(const std::string& name) {
        return intern::ObjectForward(this->name + "." + name);
    }

    /**
        Das selbe wie (*this)(name) = val; nur für Cython
    */
    template<class T>
    inline void log(const std::string& name, const T& value) {
        (*this)(name) = value;
    }

    inline void warning(const std::string& name,const std::string& val) {
        intern::LogStringStream::Wrapper(name + ".warning", enabled, DebugType::WARNING,console_out) << val;
    }

    operator bool() const {
        return enabled;
    }

private:
    std::string name;
    bool enabled;
    bool console_out;

    inline void log(const std::string& str);

    template<class T>
    inline void send(const std::string& name, const T& val);

    friend class intern::ObjectForward;
    friend class intern::LogStringStream;
};

} // namespace Debug
#define NEED_TIMER
#include "debugmacro.h"
namespace Debug {
class Timer : TimerBase {
private:
    Scope scope;
public:
    Timer(const Scope& scope, const std::string& name, bool print=false)
    : TimerBase(name, print),scope(scope)
    {}
    float current_time() const {
        return ((TimerBase*)this)->current_time();
    }
    ~Timer() {
        float ms = (boost::posix_time::microsec_clock::local_time() - this->start)
        .total_microseconds() * 0.001;

        scope(this->name) = ms;
        if(print)
            scope << this->name << " benötigte " << ms << "ms";

        print = false;
    }
};

} // namespace Debug

#endif
