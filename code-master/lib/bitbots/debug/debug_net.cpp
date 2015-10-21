#include "debug_net.hpp"
#include <iostream>

using namespace Debug::net;

Client::Client()
    : socket(io) {

    const char *addr = getenv("DEBUG_HOST");
    if(!addr)
        addr = "localhost";
    const char *port = getenv("DEBUG_PORT");
    if(!port)
        port = "6482";

    connect(addr, port);
}

void Client::connect(const std::string& host, const std::string& port) {
    socket.open(udp::v4());
    udp::resolver::query query(host, port);
    udp::resolver::iterator epit = udp::resolver(io).resolve(query);
    endpoint = *epit;
}

void Client::write(const std::string& data) {
    if(data.size() > 60000) {
        std::cout << "[Debug] UDP Nachricht zu lang." << std::endl;
        return;
    }

    socket.send_to(boost::asio::buffer(data), endpoint);
}

