#ifndef _JOINT_HPP
#define _JOINT_HPP

#include <stdint.h>

namespace Robot {

class Pose;

/**
 * \brief The joint representation for the motion.
 *
 * This is one of two joint implementations in our kinematic library.
 * This one is for the hardware representation, whether the joint is active,
 * the angle, position, speed etc..
 */
class Joint {
    private:
        bool active;
        bool changed;
        float goal;
        float speed;
        float position;
        float load;
        float p;
        float i;
        float d;
        int cid;
        float minimal;
        float maximal;

    public:
        Joint();
        Joint(float minimal, float maximal);

        void set_active(bool active);
        bool is_active() const;

        void reset();
        bool has_changed() const;

        bool set_goal(float goal);
        float get_goal() const;

        void set_speed(float speed);
        float get_speed() const;

        void set_position(float position);
        float get_position() const;

        void set_cid(int cid);
        int get_cid() const;

        void set_load(float load);
        float get_load() const;

        void set_p(int p);
        int get_p() const;

        void set_i(int i);
        int get_i() const;

        void set_d(int d);
        int get_d() const;

        void set_maximum(float maximum);
        float get_maximum() const;

        void set_minimum(float minimum);
        float get_minimum() const;

        friend class Pose;
};

inline
Joint::Joint()
    : active(0), changed(0), goal(0), speed(0), position(0), load(0), p(-1), i(-1), d(-1), cid(0), minimal(-180), maximal(180) {
}

inline
Joint::Joint(float minimal,float maximal)
    : active(0), changed(0), goal(0), speed(0), position(0), load(0), p(-1), i(-1), d(-1), cid(0), minimal(minimal), maximal(maximal) {
}

inline
bool Joint::set_goal(float goal) {
    if(goal < this->minimal or goal > this->maximal)
        return false;
    this->goal = goal;
    this->changed = true;
    this->active = true;
    return true;
}

inline
float Joint::get_goal() const {
    return goal;
}

inline
void Joint::set_speed(float speed) {
    this->speed = speed;
    this->changed = true;
}

inline
float Joint::get_speed() const {
    return speed;
}

inline
void Joint::set_position(float position) {
    this->position = position;
}

inline
float Joint::get_position() const {
    return position;
}

inline
void Joint::set_active(bool active) {
    this->active = active;
    this->changed = true;
}

inline
bool Joint::is_active() const {
    return active;
}

inline
bool Joint::has_changed() const {
    return changed;
}

inline
void Joint::reset() {
    this->changed = false;
}

inline
void Joint::set_cid(int cid) {
    this->cid = cid;
}

inline
int Joint::get_cid() const {
    return cid;
}

inline
void Joint::set_load(float load) {
    this->load = load;
}

inline
float Joint::get_load() const {
    return load;
}

inline
void Joint::set_p(int p){
    this->p = p;
    this->changed = true;
}
inline
    int Joint::get_p() const {
    return p;
}
inline
void Joint::set_i(int i){
    this->i = i;
    this->changed = true;
}
inline
    int Joint::get_i() const {
    return i;
}
inline
void Joint::set_d(int d){
    this->d = d;
    this->changed = true;
}
inline
    int Joint::get_d() const {
    return d;
}

inline
void Joint::set_maximum(float maximum) {
    this->maximal = maximum;
}

inline
float Joint::get_maximum() const {
    return maximal;
}

inline
void Joint::set_minimum(float minimum) {
    this->minimal = minimum;
}

inline
float Joint::get_minimum() const {
    return minimal;
}

} //namespace
#endif

