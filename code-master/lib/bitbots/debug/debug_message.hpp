#ifndef _MESSAGE_HPP
#define _MESSAGE_HPP

namespace Debug {
namespace com {

class Message {
private:
    std::string name, data;
    bool updatable;
    
public:
    /**
        Erzeugt eine neue Nachricht mit einem Namen und einem Datensatz.
    */
    Message(const std::string& name, const std::string& data, bool updatable)
        : name(name), data(data), updatable(updatable) {
    }
    
    const std::string& get_data() const {
        return data;
    }

    const std::string& get_name() const {
        return name;
    }
    
    bool is_updatable() const {
        return updatable;
    }
    
    /**
        Ersetzt den Inhalt der Nachricht durch 'data'.
    */
    void update(const std::string& data) {
        if(!is_updatable())
            throw std::runtime_error("no update possible");
        
        this->data = data;
    }
};

// namespace
}}

#endif

