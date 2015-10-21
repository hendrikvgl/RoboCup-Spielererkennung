#ifndef _CONCURRENT_QUEUE_HPP
#define _CONCURRENT_QUEUE_HPP

#include <queue>
#include <boost/thread/mutex.hpp>
#include <boost/thread/condition_variable.hpp>

namespace Debug{

template<typename T>
class ConcurrentQueue {
private:
    std::queue<T> backend;
    mutable boost::mutex mutex;
    mutable boost::condition_variable newdata;

public:
    void push(T const& data) {
        boost::mutex::scoped_lock lock(mutex);
        backend.push(data);
        lock.unlock();
        newdata.notify_one();
    }

    bool empty() const {
        boost::mutex::scoped_lock lock(mutex);
        return backend.empty();
    }

    void wait() const {
        boost::mutex::scoped_lock lock(mutex);
        while(backend.empty())
            newdata.wait(lock);
    }

    T pop() {
        boost::mutex::scoped_lock lock(mutex);

        T popped_value = backend.front();
        backend.pop();

        return popped_value;
    }
};

} //namespace

#endif

