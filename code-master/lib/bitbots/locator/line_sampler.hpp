#ifndef _LINE_SAMPLER_HPP
#define _LINE_SAMPLER_HPP

#include "image_point_to_location_transformer.hpp"

#include <boost/foreach.hpp>

#include <Eigen/Core>

#include <vector>
#include <iostream>
#include <utility>
#include "locator_utils.hpp"
#include "../vision/sample.hpp"
#include "../debug/debugmacro.h"
#ifndef V_SPEC
#define V_SPEC
#include <Eigen/StdVector>
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Vector2f)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Matrix2f)
#endif // V_SPEC


typedef std::pair<Eigen::Vector2f, int> VectIndex;

/**
 * Returns true, if the angle between the given vectors is lower than a given value in the Code
 */
inline
bool is_low_angle(const Eigen::Vector2f& u, const Eigen::Vector2f& v)
{
    return(( u.dot(v) )/( u.norm() * v.norm() ) > 0.98);// angle lower than ~11.5°
}
inline
bool is_low_angle(const Eigen::Vector2f& u, const Eigen::Vector2f& v, unsigned short num)
{
    return(( u.dot(v) )/( u.norm() * v.norm() ) > 1 - 0.25 / (num + 5));// angle lower than ~11.5°
}
/**
 * This variant required both vectors to be normed
 */
inline
bool is_low_angle_normed(const Eigen::Vector2f& u, const Eigen::Vector2f& v, unsigned short num)
{
    return(( u.dot(v) ) > 1 - 0.25 / (num + 5));// angle lower than ~11.5°
}

/**
 * All vectors need to be unnormalized!!!
 * Givig a normalizes direction vector makes the lines representing false things
 */
typedef struct Line{
    Eigen::Vector2f begin, end, direction;
    float length;

    Line(Eigen::Vector2f begin, Eigen::Vector2f end, Eigen::Vector2f directions)
    : length(directions.norm()), begin(begin), end(end)
    {//Direction should be normalised
        direction = directions/length;
        keep_well_directed();
    }

    Line(const Line& org, const Eigen::Matrix2f& rotate)
    :begin(rotate * org.begin), end(rotate * org.end), direction(rotate * org.direction), length(org.length)
    {
        keep_well_directed();
    }

    Line(const Eigen::Vector2f& begin, const Eigen::Vector2f& end)
    :begin(begin), end(end), direction(end - begin)
    {
        length = direction.norm();
        direction /= length;
        keep_well_directed();
    }

    Line()
    {
    }

    inline
    void keep_well_directed()
    {
        if(fabs(direction.norm() - 1) > 0.01)
        {
            std::cout<<"Bei den Linien läuft etwas schief"<<std::endl;
        }
        if(direction.x() < -0.707 ||  direction.y() < -0.707 )
        {//Keeping the lines in the right direction
            direction = - direction;
            Eigen::Vector2f tmp = end;
            end = begin;
            begin = tmp;
        }
    }
}Line;

typedef struct Circle{
    Eigen::Vector2f midpoint;
    float radius;

    Circle(Eigen::Vector2f midpoint, float radius)
    : midpoint(midpoint), radius(radius)
    {

    }
    Circle(const Circle& org, const Eigen::Matrix2f& rotate)
    : midpoint(rotate * org.midpoint), radius(org.radius)
    {

    }
    Circle()
    {
    }
} Circle;

typedef struct Line_Samples{//Das sind Adressen -> unsicher!!
    std::vector<Line>& lines;
    std::vector<Circle>& circles;
    std::vector<Eigen::Vector2f>& points;

    Line_Samples(std::vector<Line>& lines, std::vector<Circle>& circles, std::vector<Eigen::Vector2f>& points)
    :lines(lines), circles(circles), points(points)
    {

    }

}Line_Samples;


namespace Location{
namespace pa = Debug::Paint;

class Line_Sampler{
private:

mutable Debug::Scope m_debug;//Dem Locator ein debug Objekt spendiert.//ggf Entfernen siehe Konstruktor
std::vector<pa::Shape> m_debug_shapes;
std::vector<Vision::Sample::LineSample> projected;
std::vector<Line> lines;
std::vector<Eigen::Vector2f> points;
std::vector<Circle> circles;
Line_Samples line_samples;
Image_Point_To_Location_Transformer& transformer;

/*
 * An idea to find a possible alone standing point on the field
 * Every center of gravity marks it's location with a point index, when alone in area
 * or -1 when it's already marked
 * Let's look at an area of 6x6 meter using an intervall of 0.25 meter for
 * every point
 */
int point_locations[25][25];

    /**
     * A little helper pushing debug_shapes for orientation where the other
     * shapes could be
     */
    inline
    void print_debug_shape_orientation();

    /**
     * Mark the area where the point is with its cluster index + 1
     * When another point is in this area Mark it with -1
     * 0 means there are no points in this area.
     */
    inline
    void mark_location(const Eigen::Vector2f& point, const int index);

    /**
     * Init locations with 0
     */
    inline
    void init_point_locations()
    {
        for(int i = 0; i < 25; ++i)
        {
            for(int j = 0; j < 25; ++j)
            {
                point_locations[i][j] =((int)0);
            }
        }
    }

    /**
     * Searches for an area where is only on point and which has no marked neighbours
     */
    inline
    void find_lonely_point(const std::vector<int>& cluster_begin_indices);

    /**
     * Makes some things to provide false detected lines.
     * Can be extendet with filtering out false circles
     */
    inline
    void improve_sample_quality();

    /**
     * Goes through the lines and finds parallel ones. Then sorts out
     * parallel overlapping lines but keeps the "sum" of overlapping lines
     * Then reduces the lines to two almost parallel components
     */
    inline
    void find_parallel_lines();

    /**
     * Requires two Lines laying on a straight line. Then this Method
     * returns a Line representing the "sum" of both
     * v represents the "distance" between the two beginnings of the lines
     * v is negative, when the first line lays in front of the second one
     * relative two teir direction and the robot
     */
    inline
    Line sum_up_lines(const Line& first, const Line& second, float v);

    /**
     * Checks wheater there are lines surrounding a circle, what could give
     * a big error on position estimation
     */
    inline
    void handle_circles();

    /**
     * Tries to filter out points, that can't be field points
     */
    inline
    void handle_points();

    /**
     * Projects the points so that they are laying in a 2D coordinate system with
     * the robot as origin
     */
    inline
    void project_points(const std::vector<Vision::Sample::LineSample>& line_points, std::vector<int>& cluster_begin_indices);

    /**
     * Calculates a chain of centers of gravity of connected points.
     * Uses the parent Structure of Line_Clustering
     * This Method also identifies the clusters.
     */
    inline
    void chain_cog(int index, const int length, std::vector<Eigen::Vector2f>& cogs, std::vector<char>& visited, const int marking_index);

    /**
     * Calculates a single center of gravity using the parent structure.
     * The given clusters don't garantee neighboured points to be relatively
     * close to each other in the cluster. That's why this uses a build up structure
     * of parent points.
     */
    inline
    VectIndex cog(int index, const int length, std::vector<char>& visited);

    /**
     * Return the Matrix representing the robot's center to floor
     */
    Eigen::Matrix4f get_floor_matrix() const;

    /**
     * Projects a vector so that it has the correct position on a debug image
     */
    inline
    Eigen::Vector2f project_vector_for_debug(const Eigen::Vector2f& v);

    /**
     * Validates the structure a a component of connected points or better
     * centers of gravity.
     * This Method tries to match lines as long as the angle of the given points
     * is quite low.
     * After that, check wheater it could be a circle
     */
    inline
    bool check_structure(const std::vector<Eigen::Vector2f>& cogs, bool recursive = true);

    /**
     * Validates wheather a strcture could be part of a circle.
     * Calculates possible midpoints and counts the number of point with a specific distance
     * to the midpoint
     */
    inline
    bool check_circle(const std::vector<Eigen::Vector2f>& circle_points);


    inline
    float abs(float t)
    {
        return t<0? -t:t;
    }



public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    Line_Sampler(Image_Point_To_Location_Transformer& transformer)
    :m_debug("Locator.Sampling"), transformer(transformer),
    line_samples(lines, circles, points)
    {
    }

    /**
     * Returns the transformer
     */
    Image_Point_To_Location_Transformer& get_transformer()
    {
        return transformer;
    }


    void update(const std::vector<Vision::Sample::LineSample>& line_points);

#define CONST
    /**
        Gibt eine Referenz auf die debug_shapes zurück
    */
    CONST std::vector<pa::Shape>& get_debug_shapes() CONST
    {
        return m_debug_shapes;
    }

    /**
     * Returns the matched lines
     * Every line is directed from "left to right" or upwards
     */
    CONST Line_Samples& get_line_samples() CONST
    {
        return line_samples;
    }
#undef CONST

};

}//namespace

#endif
