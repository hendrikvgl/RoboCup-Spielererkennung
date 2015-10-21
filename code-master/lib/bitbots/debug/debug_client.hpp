#ifndef _DEBUG_CLIENT_HPP
#define _DEBUG_CLIENT_HPP

#include "debug.hpp"
#include "debug_net.hpp"
#include "debug_message.hpp"

#include <utility>
#include <memory>
#include <thread>
#include <boost/utility.hpp>
#include <boost/thread/mutex.hpp>

#include "concurrent_queue.hpp"

using std::shared_ptr;
using std::make_shared;

namespace Debug {
namespace com {

template<class ClientBackend>
class Client : boost::noncopyable {
private:
    mutable boost::mutex mutex;

    std::thread thread;
    std::shared_ptr<ClientBackend> client;
    std::map<std::string, shared_ptr<Message> > messages;
    ConcurrentQueue<shared_ptr<Message> > queue;
    bool terminate_flag;

    void send_message();
public:
    Client() : thread(std::thread(std::ref(*this))) {
        terminate_flag = false;
    }
    ~Client();

    // Thread Funktion
    void operator()();

    /**
        Hier kann eine Nachricht übergeben werden, die dann im ClientThread
        über das Netzwerk vermittelt wird.
    */
    void write(const std::string& name, const std::string& data, bool updatable);
};

template<class ClientBackend>
void Client<ClientBackend>::operator()() {
    bool show_error = true;
    while(true) {
        try {
            client = make_shared<ClientBackend>();
            show_error = true;

            while(!terminate_flag) {
                queue.wait();
                send_message();
            }
            // wait for termination
            return;
        } catch(const std::exception& e) {
            if(show_error) {
                std::clog << "[DebugThread] " << e.what() << std::endl;
                show_error = false;
            }

            sleep(2);
        }
    }
}

template<class ClientBackend>
Client<ClientBackend>::~Client() {
    terminate_flag = true;
    {
        boost::mutex::scoped_lock lock(mutex);
        if(queue.empty()) {
            Message m("","",false);
            queue.push(make_shared<Message>(m));
        }
    }
    thread.join();
}


template<class ClientBackend>
void Client<ClientBackend>::send_message() {
    std::string data;
    //terminate immediately when in destructor
    if(terminate_flag) return;
    {
        boost::mutex::scoped_lock lock(mutex);

        shared_ptr<Message> msg = queue.pop();
        if(msg->is_updatable())
            messages.erase(msg->get_name());

        data = msg->get_data();
    }

    client->write(data);
}

template<class ClientBackend>
void Client<ClientBackend>::write(const std::string& name,
        const std::string& data, bool updatable) {

    boost::mutex::scoped_lock lock(mutex);

    // std::cout << "[Debug] " << name << " (" << data.size() << " bytes)" << std::endl;

    if(updatable && messages.count(name) > 0) {
        // Wir können einfach eine bestehende Nachricht updaten
        messages[name]->update(data);
    } else {
        // Wir erzeugen eine neue Nachricht
        shared_ptr<Message> msg = make_shared<Message>(name, data, updatable);
        queue.push(msg);

        // Nachricht merken, um sie später updaten zu können
        if(updatable)
            messages[name] = msg;
    }
}

// namespace
}}

#endif

