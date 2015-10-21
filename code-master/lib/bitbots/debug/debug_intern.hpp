#ifndef _DEBUG_INTERN_HPP
#define _DEBUG_INTERN_HPP

#include <sstream>
#include <iostream>
#include <stdlib.h>
#include <memory>

#include <boost/utility.hpp>

#include <boost/thread/locks.hpp>
#include <boost/thread/recursive_mutex.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/posix_time/posix_time_io.hpp>

#include "debug_type_info.hpp"
#include "debug_serialize.hpp"

#include <boost/format.hpp>
#include <boost/filesystem.hpp>
#include <boost/iostreams/device/file.hpp>
#include <boost/iostreams/filtering_stream.hpp>
#include <boost/iostreams/filter/zlib.hpp>
#include <boost/asio/ip/host_name.hpp>

namespace Debug {
namespace intern {

using std::make_shared;
using namespace boost::posix_time;

static bool debug_enable = getenv("DEBUG") != nullptr && getenv("DEBUG")[0] == '1';
static bool nolog_enable = getenv("NO_LOG") != nullptr && getenv("NO_LOG")[0] == '1';

// USE THIS REGULARLY
static std::string HOSTNAME(boost::asio::ip::host_name());

// USE THIS FOR SIMULATING 2D // @ Robert 08.04.2014:I had many trouble with strings initialized from nullptr.
static bool env_hostname_is_set = getenv("HOSTNAME") != nullptr;
static std::string HOSTNAME_ENV = env_hostname_is_set ? std::string(getenv("HOSTNAME")) : std::string("");

extern std::ofstream LOGFILE;
extern bool LOGFILE_is_open;

void debug_send_data(const std::string& name, const std::string& data, bool force);

/**
 * Diese Methode serialisiert eine Nachricht und sendet
 * sie an einen möglichen Debug Empfänger
 */
template<class T>
void debug_send(const std::string& name, const u_int8_t type,
        const T& object) {

    if(!debug_enable)
        return;

    std::stringstream stream(std::ios_base::binary | std::ios_base::out);
    {
        // gzip Stream initialisieren
        boost::iostreams::filtering_stream<boost::iostreams::output> out;
        out.push(boost::iostreams::zlib_compressor());
        out.push(stream);

        // serialisieren
        if(!env_hostname_is_set){
            Serialize::OutputArchive ar(out);
            ar & (HOSTNAME + "::" + name);
            ar & type;
            ar & object;
        } else {abort();
            Serialize::OutputArchive ar(out);
            ar & (HOSTNAME_ENV + "::" + name);
            ar & type;
            ar & object;
        }
    }

    const std::string& data = stream.str();
    if(not nolog_enable)
    {
        if(not LOGFILE_is_open) {
            LOGFILE_is_open = true;
            // Logfile im $HOME Ordner öffnen
            const char *home = getenv("HOME");
            if(!home)
                throw std::runtime_error("HOME nicht gesetzt!");
            system("mkdir $HOME/debug/");
            std::string filename = str(boost::format("%s/debug/darwin-debug-%s.gz") % home % to_iso_string(microsec_clock::local_time()));
            LOGFILE.open(filename.c_str(), std::ios::out);
        }

        if(LOGFILE_is_open and LOGFILE.good()) {
            // Zeit, Größe und Daten schreiben
            uint32_t size = data.size();
            uint64_t now = microsec_clock::local_time().time_of_day().total_milliseconds();

            LOGFILE.write((const char*)&now, 8);
            LOGFILE.write((const char*)&size, 4);
            LOGFILE.write(data.c_str(), size);
        }
    }
    // versenden
    debug_send_data(name, stream.str(), (type != (uint8_t)DebugType::LOG) && (type != (uint8_t)DebugType::WARNING));
}

/**
 * Ein einfacher StringStream, der bei Zerstörung seinen Inhalt über
 * debug_send als Log versendet.
 */
class LogStringStream : boost::noncopyable {
private:
    std::stringstream stream;
    std::string name;
    uint8_t type;
    bool enabled;
    bool console_out;

public:
    LogStringStream(const std::string& name, bool enabled, uint8_t type = DebugType::LOG, bool console_out = true)
            : name(name), type(type), enabled(enabled), console_out(console_out) {
    }

    ~LogStringStream() {
        //static boost::recursive_mutex mutex;

        if(enabled) {
            debug_send(name, type, stream.str());
        } else {
            static boost::recursive_mutex mutex;
        boost::lock_guard<boost::recursive_mutex> lock(mutex);

            boost::posix_time::ptime now(boost::posix_time::second_clock::local_time());

            // Log
            std::ofstream output("/root/debug.log", std::ios::app);
            output << boost::posix_time::to_simple_string(now)
                << " [" << name << "] " << stream.str() << std::endl;
        }
        if(console_out) {
            if (type == (uint8_t)DebugType::LOG)
            {
                std::clog << "[" << name << "] " << stream.str() << std::endl;
            }
            else
            {
                std::clog << "\033[1;31m[" << name << "] " << stream.str() <<  "\033[0m" << std::endl;
            }
        }
    }

    template<class T>
    void operator<<(const T& val) {
        if (stream.str().size() > 0 && *(stream.str().end() - 1) != ' ')
            stream << " ";

        stream << val;
}

    class Wrapper;
};

/**
 * Hilfsklasse, die einen LogStringStream in einem std::shared_ptr hält
 * und diesen erst zerstört, wenn die letzte Instanz kaputt ist.
 * Leitet operator<< an den StringStream weiter.
 */
class LogStringStream::Wrapper {
private:
    std::shared_ptr<LogStringStream> dos;

public:
    Wrapper(const std::string& name, bool enabled, uint8_t type=DebugType::LOG, bool console_out = true)
    : dos(std::make_shared<LogStringStream>(name, enabled, type, console_out)) {
    }

    template<class T>
    Wrapper& operator<<(const T& val) {
        *dos << val;
        return *this;
}
};

/**
 * Versendet ein beliebiges Objekt über debug_send durch den << oder =
 * Operator.
 */
class ObjectForward {
private:
    std::string name;

public:
    explicit ObjectForward(const std::string& name)
            : name(name) {
    }

    template<class T> void operator<<(const T& obj) const {
        debug_send(name, TypeInfo<T>::Type, obj);
    }

    template<class T> void operator=(const T& obj) const {
        operator<<(obj);
    }

    void operator<<(const char* str) const {
        operator<<(std::string(str));
    }

    void operator=(const char* str) const {
        operator=(std::string(str));
    }
};

// namespace
}
}

#endif
