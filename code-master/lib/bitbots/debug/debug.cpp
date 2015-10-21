#include "debug.hpp"
#include "debug_net.hpp"
#include "debug_message.hpp"
#include "debug_client.hpp"

#include <memory>

using Debug::com::Client;

static std::shared_ptr<Client<Debug::net::Client> > client;

static void debug_start_client() {
    client = make_shared<Client<Debug::net::Client> >();
}

namespace Debug {
namespace intern {

std::ofstream LOGFILE;
bool LOGFILE_is_open = false;

void debug_send_data(const std::string& name, const std::string& data, bool updatable) {
    if(debug_enable) {
        if(!client)
            debug_start_client();

        client->write(name, data, updatable);
    }
}

} } // namespace

