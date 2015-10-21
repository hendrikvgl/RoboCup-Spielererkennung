#ifndef _DEBUG_NET_HPP
#define _DEBUG_NET_HPP


#include <boost/asio.hpp>
#include <boost/array.hpp>

namespace Debug {
namespace net {

using namespace boost::asio;
using boost::asio::ip::udp;

class Client {
private:
	io_service io;
    udp::socket socket;
    udp::endpoint endpoint;

    void connect(const std::string& host, const std::string& port);
public:
	Client();
    void write(const std::string& data);
};

// namespace
}}

#endif

