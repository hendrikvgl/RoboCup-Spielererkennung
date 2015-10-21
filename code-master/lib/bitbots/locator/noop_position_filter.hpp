#ifndef _NOOB_POSITION_FILTER_HPP
#define _NOOB_POSITION_FILTER_HPP

#include <Eigen/Core>
#include <vector>
#include <iostream>
#include <../debug/debug.hpp>
#include "../debug/debugmacro.h"
#ifndef V_SPEC
#define V_SPEC
#include <Eigen/StdVector>
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Vector2f)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Matrix2f)
#endif // V_SPEC

namespace Location{

class Noob_Position_Filter{

typedef Eigen::Matrix<float,3,2> Position;
public:
    Noob_Position_Filter()
    : position_decreasing_factor(0.9), way_moved(0,0,0), m_debug("Locator.Filter")
    {
        current_position.col(0)<< 0, 0, 0;
        current_position.col(1)<< 0, 0, 0;
    }

    ~Noob_Position_Filter()
    {

    }

private:
std::vector<Position > positions;
Position current_position;
const float position_decreasing_factor;
std::vector<Eigen::Matrix2f> position_information;
Eigen::Vector3f way_moved;
mutable Debug::Scope m_debug;

    /**
     * Goes through the list of positions which are likly, because of the
     * seen image and filters them witch it's field model.
     * Positions outside the field and outside the known own location will
     * be ignorde.
     */
    inline
    void filter_impossible_positions(std::vector<Position >& suggestions);

    /**
     * Updates all remembered positions with current motion movement.
     * Then decreases the niceness of them all.
     */
    inline
    void update_positions(Eigen::Vector3f& movement, float position_decreasing_factor);

    /**
     * Intern method to find an overlay in two ranges.
     */
    inline
    Eigen::Matrix<float, 1, 2> find_overlay(const Eigen::Matrix<float, 1, 2>& org_pos, const Eigen::Matrix<float, 1, 2>& pos);

    /**
     * Matches the position suggestions with the remembered positions.
     * If there is a match, the remembered position is updates
     * else will remember new position suggestion
     */
    inline
    void match(const std::vector<Position >& suggestions);

    /**
     * Goes through all remembered positions and finds the best one.
     * Then deletes those who are worse than an implemented criteria
     */
    inline
    void set_position();

    /**
     * Updates the additional position information by incresing the range
     * linear with the current movement. When the ares is to large, it will
     * be ignored
     */
    void update_information(Eigen::Vector2f movement);

    /**
     * Updates the total movement of the roboter.
     */
    inline
    void update_global_movement(Eigen::Vector3f& movement);

public:

    /**
     * Adds an area to the additional information, where the robot could be
     */
    inline
    void set_position_information(Eigen::Matrix2f& position)
    {
        position_information.push_back(position);
    }

    /**
     * Clears the additional position information like
     * "I'm in my own half"
     */
    inline
    void reset_information()
    {
        position_information.clear();
        way_moved = Eigen::Vector3f(0,0,0);
    }

    /**
     * Overrideing all additional position information
     */
    void set_additional_position_info(const std::vector<Eigen::Matrix2f>& position_limitations)
    {
        position_information.~vector<Eigen::Matrix2f>();
        position_information = position_limitations;
    }

    /**
     * Sets the global ball position
     * !!!Still not implemented!!!
     */
    void set_ball_pos(Eigen::Vector2f)
    {

    }

    /**
     * Sets the global goal position
     * !!!Still not implemented!!!
     */
    void set_global_ball_pos(Eigen::Vector2f)
    {

    }

    /**
     * Starts a position update cycle
     */
    void update(const std::vector<Position >& position_suggestions, Eigen::Vector3f movement);

    /**
     * Returns the current position suggestion
     * it does'nt contain qaulity information
     */
    inline
    Eigen::Vector3f get_position()
    {
        Eigen::Vector3f result;
        result(0) = (current_position(0,0) + current_position(0,1) ) / 2;
        result(1) = (current_position(1,0) + current_position(1,1) ) / 2;
        result(2) = current_position(2,0);
        return result;
    }

};


}//namespace

#endif
