#ifndef _LINE_MATCHER_HPP
#define _LINE_MATCHER_HPP


//#include <boost/foreach.hpp>

#include <Eigen/Core>

#include <vector>
#include <iostream>
#include "line_sampler.hpp"
#include <../debug/debug.hpp>
#include "../debug/debugmacro.h"
#ifndef V_SPEC
#define V_SPEC
#include <Eigen/StdVector>
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Vector2f)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Matrix2f)
#endif // V_SPEC

namespace Location{
namespace pa = Debug::Paint;

const static float pi = 3.1415926;

const static Eigen::Vector2f horizontal(1,0);
const static Eigen::Vector2f vertikal(0,1);

const static float circle_position_error = 0.25;
const static float circle_evaluation_faktor = 0.5;
const static float point_position_error = 0.25;
const static float point_evaluation_faktor = 0.5;

class Line_Matcher{

public:

    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    Line_Matcher(Line_Samples fieldmodel)
    :fieldmodel(fieldmodel), m_debug("Locator")
    {
    }

    ~Line_Matcher()
    {
        delete &fieldmodel.lines;
        delete &fieldmodel.circles;
        delete &fieldmodel.points;
    }

    void update(const Line_Samples& line_samples);

    std::vector<Eigen::Matrix<float, 3, 2> > get_suggested_positions()
    {
        return possible_positions;
    }

#define CONST
    CONST std::vector<pa::Shape>& get_debug_shapes() CONST
    {
        return m_debug_shapes;
    }
#undef CONST


private:

mutable Debug::Scope m_debug;
std::vector<pa::Shape> m_debug_shapes;
std::vector<Eigen::Matrix<float, 3, 2> > possible_positions;
const Line_Samples fieldmodel;

    /**
     * Tries to find locations on the field, where the robot can see lines at the
     * samples positions.
     * Those positions are added in possible_locations
     */
    inline
    float match_samples(Line_Samples& projected_samples, float angle, int longest_line);

    /**
     * Matches a circle to verify a position
     */
    inline
    float match_circles(std::vector<Circle>& seen_circles, Eigen::Matrix2f& pos);

    /**
     * Tries to match the seen located point with the known point positions
     * on the field. Return a weighted float to compare matching distance
     */
    inline
    float match_points(const std::vector<Eigen::Vector2f>& seen_points, Eigen::Matrix2f& pos);

    /**
     * Tries to project the samples, so that the x or y coordinate of the lines direction is 0.
     * Returns the angular, wich was used for this projection.
     * Returned angle is in radiant
     */
    inline
    float normalize_data(const Line_Samples& line_samples, Line_Samples& projected_samples, int longest_line);

    /**
     * Returns true, when the angle is small enough
     */
    inline
    bool is_low_angle(const Eigen::Vector2f& u, const Eigen::Vector2f& v)
    {
        return(( u.dot(v) )/( u.norm() * v.norm() ) > 0.98);// angle lower than ~9.9°
    }

    /**
     * Rotates every sample, line, circle and point
     */
    inline
    void rotate_samples(const Line_Samples& line_samples, Line_Samples& projected_samples, float angle);

    /**
     * Matches one line, with a given samples
     */
     inline
     bool match_line(const Line& current, const Line& field_line, Eigen::Matrix2f& pos);

     /**
      * Finds an area within both arguments
      * When there is no overlay this method returns the beginnig value -1 twice
      */
    inline
    Eigen::Matrix<float, 1, 2> find_overlay(const Eigen::Matrix<float, 1, 2>& org_pos, const Eigen::Matrix<float, 1, 2>& pos);

    /**
     * Returns the index of the longest line
     */
    inline
    int get_longest_line(std::vector<Line>& lines);

    /**
     * Goes throug the possible Positions and sends a selection to debug UI
     */
    inline
    void print_debug_shapes(float max_matching_distance, const Line_Samples& line_samples);

};






}//namespace

#endif
