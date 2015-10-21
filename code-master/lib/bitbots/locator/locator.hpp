#ifndef _LOCATOR_HPP
#define _LOCATOR_HPP

#include <boost/foreach.hpp>

#include <Eigen/Core>

#include <vector>
#include <iostream>
#include <cmath>

#include "image_point_to_location_transformer.hpp"
#include "../debug/debug.hpp"
#include "line_sampler.hpp"
#include "line_matcher.hpp"
#include "noop_position_filter.hpp"
#include "../debug/debugmacro.h"
#ifndef V_SPEC
#define V_SPEC
#include <Eigen/StdVector>
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Vector2f)
EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Matrix2f)
#endif // V_SPEC

#define foreach BOOST_FOREACH


namespace Location{
namespace pa = Debug::Paint;

class Locator{

private:
Line_Sampler sampler;
Line_Matcher matcher;
Noob_Position_Filter filter;
mutable Debug::Scope m_debug;//Dem Locator ein debug Objekt spendiert.//ggf Entfernen siehe Konstruktor
//mutable Debug::Scope vision_fake_debug;//Dem Locator ein debug Objekt spendiert.//ggf Entfernen siehe Konstruktor

public:

    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    Locator(Image_Point_To_Location_Transformer& transformer)
    :m_debug("Locator"),/*vision_fake_debug("Vision"),*/ matcher(make_field_model())
    , sampler(transformer)
    {//Wenn Feldmodell geändert wird Line_Matcher::match_samples anpassen
        print_debug_information(__FILE__);
    }

    Line_Samples make_field_model();

    inline
    void say_robot_in_own_half()
    {
        Eigen::Matrix2f m;
        m.row(0) << -3, 0;
        m.row(1) <<  -2, 2;
        set_position_information(m);
    }

    inline void say_robot_out_of_field()
    {
        say_robot_out_of_field_long_side();
        say_robot_out_of_field_short_side();
    }

    inline void say_robot_out_of_field_long_side()
    {
        Eigen::Matrix2f l;
        l.row(0) << -3.7, 3.7;
        l.row(1) <<  2, 2.7;
        set_position_information(l);
        Eigen::Matrix2f r;
        r.row(0) << -3.7, 3.7;
        r.row(1) <<  -2.7, 2;
        set_position_information(r);
    }

    inline void say_robot_out_of_field_short_side()
    {
        Eigen::Matrix2f v;
        v.row(0) << -3.7, -3;
        v.row(1) <<  -2.7, 2.7;
        set_position_information(v);
        Eigen::Matrix2f h;
        h.row(0) << 3, 3.7;
        h.row(1) <<  -2.7, 2.7;
        set_position_information(h);
    }

    inline void say_robot_is_goalie()
    {
        Eigen::Matrix2f m;
        m.row(0) << -3, -2.4;
        m.row(1) <<  -1.1, 1.1;
        set_position_information(m);
    }

    inline
    void set_position_information(Eigen::Matrix2f& position)
    {
        filter.set_position_information(position);
    }

    inline
    void reset_information()
    {
        filter.reset_information();
    }

    /**
     * Gives a new transformer to the sampler
     */
    void set_transformer(Image_Point_To_Location_Transformer& transformer)
    {
        //Getting the address of the sampler
        Line_Sampler* address = &sampler;
        //Destroying the old Object
        sampler.~Line_Sampler();
        // Calling the constructor with the placement-new
        new(address) Line_Sampler(transformer);
    }

    /**
     * Returns the transformer
     */
    Image_Point_To_Location_Transformer& get_transformer()
    {
        return sampler.get_transformer();
    }

    /**
    *    Setzt die aktuelle Stellung der Gelenke des Roboters.
    */
    void set_pose(const Robot::Pose& pose) {
        Image_Point_To_Location_Transformer& transformer = const_cast<Image_Point_To_Location_Transformer&>(sampler.get_transformer());
        transformer.update_pose(pose);
    }

    /**
    *    Berechnet die Position des Roboters aus eine Menge von Linien Punkten
    */
    void update(const std::vector<Vision::Sample::LineSample>& line_points, Eigen::Vector3f movement = Eigen::Vector3f(0,0,0))
    {
        DEBUG_TIMER(1, "Update");
        {
            DEBUG_TIMER(1, "Update.1Samples");
            sampler.update(line_points);
        }
        {
            DEBUG_TIMER(1, "Update.Matching");
            matcher.update(sampler.get_line_samples());
        }
        {
            DEBUG_TIMER(1, "Update.Positioning");
            filter.update(matcher.get_suggested_positions(),movement);
        }
        Eigen::Vector3f position = filter.get_position();
        export_debug(position);
    }

    void export_debug(Eigen::Vector3f& position)
    {
        DEBUG(2, "Position.X", position.x());
        DEBUG(2, "Position.Y", position.y());
        DEBUG(2, "Position.Z", position.z());
        //vision_fake_debug("DebugImage.Shapes_Locator") = sampler.get_debug_shapes();
        //debug("Field.Shapes") = sampler.get_debug_shapes();
        const std::vector<pa::Shape>& debug_shapes_matcher = matcher.get_debug_shapes();
        std::vector<pa::Shape> m_debug_shapes;
        Eigen::Matrix2f rot;
        rot<<cos(position.z()), sin(position.z()), -sin(position.z()), cos(position.z());
        //std::cout<<rot<<std::endl;
        foreach(const Line& line, sampler.get_line_samples().lines)
        {
            Eigen::Vector2f begin = position.head<2>() + rot * line.begin;
            Eigen::Vector2f end = position.head<2>() + rot * line.end;

            //Eigen::Vector2f begin = position.head<2>() + Eigen::Vector2f(sin(line.begin(1)) + cos(line.begin(0)), cos(line.begin(1)) - sin(line.begin(0)));
            //Eigen::Vector2f end = position.head<2>() + Eigen::Vector2f(sin(line.end(1)) + cos(line.end(0)), cos(line.end(1)) - sin(line.end(0)));
            DEBUG_SHAPES3(pa::line(begin, end,pa::Red));
        }
        foreach(const Circle& circle, sampler.get_line_samples().circles)
        {
            Eigen::Vector2f midpoint = position.head<2>() + rot * circle.midpoint;
            DEBUG_SHAPES3(pa::circle(midpoint, circle.radius,pa::Red));
        }
        foreach(const Eigen::Vector2f& point, sampler.get_line_samples().points)
        {
            Eigen::Vector2f point_pos = position.head<2>() + rot * point;
            DEBUG_SHAPES3(pa::point(point_pos,pa::Red));
        }
        foreach(const pa::Shape& shape, debug_shapes_matcher)
        {
            DEBUG_SHAPES3(shape);
        }
        DEBUG_SHAPES1(pa::robot(position, pa::Green));
        DEBUG(3, "Field.Shapes", m_debug_shapes);
        DEBUG(3, "Field.Draw", true);
    }

    Eigen::Vector3f get_position()
    {
        return filter.get_position();
    }
#define CONST
    /**
    *    Gibt eine Referenz auf die debug_shapes zurück
    */
    inline
    CONST std::vector<pa::Shape>& get_debug_shapes() CONST {
        return sampler.get_debug_shapes();
    }
#undef CONST


};

}//namespace

#endif
