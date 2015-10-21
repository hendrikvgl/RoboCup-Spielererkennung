#include <Eigen/Core>

#include <vector>
#include <iostream>
#include <cmath>
#include <boost/foreach.hpp>

#include "line_matcher.hpp"
#include "locator_utils.hpp"


#define foreach BOOST_FOREACH


using namespace Location;
typedef Eigen::Matrix<float, 3, 2> Matrix3_2f;

void Line_Matcher::update(const Line_Samples& line_samples)
{
    possible_positions.clear();

    float angle = 0;//The angle is in radiant
    std::vector<Line>lines;
    std::vector<Circle> circles;
    std::vector<Eigen::Vector2f>points;
    Line_Samples projected_samples(lines, circles, points);
    int longest_line = get_longest_line(line_samples.lines);

    //Normalising the lines a first time
    angle += normalize_data(line_samples, projected_samples, longest_line);
    //Matching
    float max_matching_distance = match_samples(projected_samples, angle, longest_line);
    //Rotate
    rotate_samples(line_samples, projected_samples, (angle = angle + pi/2));
    //Matching again
    max_matching_distance = std::max(max_matching_distance,
        match_samples(projected_samples, angle, longest_line));

    print_debug_shapes(max_matching_distance, line_samples);
}

float Line_Matcher::match_samples(Line_Samples& projected_samples, float angle, int longest_line_index)
{
    if(longest_line_index < 0)
    {
        return 0;
    }
    const std::vector<Line>& lines = projected_samples.lines;
    const Line& longest_line = lines[longest_line_index];
    float max_matching_distance = 0;
    for(int i = 0; i < fieldmodel.lines.size(); ++i)
    {
        if(fieldmodel.lines[i].length < 0.95 * longest_line.length)
        {
            continue;
        }
        if(is_low_angle(longest_line.direction, fieldmodel.lines[i].direction))
        {
            Eigen::Matrix2f pos;//find possible initial position
            pos.col(0)=fieldmodel.lines[i].begin - longest_line.begin;
            pos.col(1)=fieldmodel.lines[i].end - longest_line.end;
            //Matching all the other Lines
            float matching_distance = 0;
            for(int j = 0; j < lines.size(); ++j)
            {
                Line current_line = lines[j];
                if(is_low_angle(current_line.direction, horizontal))//Wenn Feldmodell geändert wird anpassen
                {
                    for(int k = 0; k < 6; ++k)
                    {
                        if(match_line(current_line, fieldmodel.lines[k], pos))
                        {
                            matching_distance += current_line.length;
                        }
                    }
                }
                else if(is_low_angle(current_line.direction, vertikal))//Wenn Feldmodell geändert wird anpassen
                {
                    for(int k = 6; k < 11; ++k)
                    {
                        if(match_line(current_line, fieldmodel.lines[k], pos))
                        {
                            matching_distance += current_line.length;
                        }
                    }
                }
            }//all Lines matched
            matching_distance += match_circles(projected_samples.circles, pos);
            //Match Points
            matching_distance += match_points(projected_samples.points, pos);

            Matrix3_2f position;
            position.topLeftCorner<2,2>() = pos;
            position.row(2)<<angle, matching_distance;//Unsauber wegen verschiedenen Sachen in einem Objekt...BLAAA :(
            max_matching_distance = std::max(max_matching_distance, matching_distance);
            possible_positions.push_back(position);
        }
    }
    return max_matching_distance;
}

bool Line_Matcher::match_line(const Line& seen_line, const Line& field_line, Eigen::Matrix2f& pos)
{//Match auf x, y parametrisieren?
    //Eigen::Vector2f begin = seen_line.begin + pos.col(0);

    bool x_ok, y_ok = false;
    Eigen::Matrix2f position;//find possible initial position
    position.col(0)=field_line.begin - seen_line.begin;
    position.col(1)=field_line.end - seen_line.end;
    Eigen::Matrix<float, 1, 2> overlay_y = find_overlay(pos.row(1), position.row(1));
    y_ok = (overlay_y(0) >= pos.row(1)(0));
    Eigen::Matrix<float, 1, 2> overlay_x = find_overlay(pos.row(0), position.row(0));
    x_ok = (overlay_x(0) >= pos.row(0)(0));

    if(x_ok && y_ok)
    {
        pos.row(0) = overlay_x;
        pos.row(1) = overlay_y;
        return true;
    }
    return false;
}

Eigen::Matrix<float, 1, 2> Line_Matcher::find_overlay(const Eigen::Matrix<float, 1, 2>& org_pos, const Eigen::Matrix<float, 1, 2>& pos)
{
    float begin = org_pos(0) > pos(0)? org_pos(0): pos(0);//Using max
    float end = org_pos(1) < pos(1)? org_pos(1): pos(1);//Using min
    if(begin < end + 0.25)//Allow a little mistake
    {
        return Eigen::Matrix<float, 1, 2> (begin, std::max(begin,end));
    }
    else
    {
        return Eigen::Matrix<float, 1, 2>(org_pos(0)-1, org_pos(1)-1);
    }
}

float Line_Matcher::match_circles(std::vector<Circle>& seen_circles, Eigen::Matrix2f& pos)
{
    if(seen_circles.size() == 0)
    {
        return 0;
    }
    const Circle& mid_circle = fieldmodel.circles[0];
    float max_matching_distance = 0;
    int index = -1;
    Eigen::Matrix2f best_pos;
    for(int i = 0; i < seen_circles.size(); ++i)
    {
        if(fabs(seen_circles[i].radius - mid_circle.radius) < 0.25 * mid_circle.radius)
        {//sort out circles that are unusable//maximum 25% difference to original radius
            continue;
        }

        Eigen::Vector2f position = mid_circle.midpoint - seen_circles[i].midpoint;
        Eigen::Matrix2f check_pos;
        static const Eigen::Vector2f circle_error = Eigen::Vector2f(circle_position_error, circle_position_error);
        check_pos.col(0) = position - circle_error;
        check_pos.col(1) = position + circle_error;

        check_pos.row(0) = find_overlay(check_pos.row(0), pos.row(0));
        check_pos.row(1) = find_overlay(check_pos.row(1), pos.row(1));
        //Verify that there is an overlay in possible positions
        if(!(check_pos(0,0) < position(0) - circle_position_error || check_pos(1,0) < position(1) - circle_position_error ))
        {
            if(max_matching_distance < 2*pi*seen_circles[i].radius)
            {
                best_pos = check_pos;
                max_matching_distance = 2*pi*seen_circles[i].radius;
                index = i;
            }
        }
    }
    if(index != -1)
    {
        pos = best_pos;//Setting the specific position
    }
    return circle_evaluation_faktor * max_matching_distance;
}

float Line_Matcher::match_points(const std::vector<Eigen::Vector2f>& seen_points, Eigen::Matrix2f& pos)
{
    if(seen_points.size() == 0)
    {
        return 0;
    }
    int matching_count = 0;
    Eigen::Matrix2f best_pos = pos;
    for(int i = 0; i < seen_points.size(); ++i)
    {
        for(int j = 0; j < fieldmodel.points.size(); ++j)
        {
            Eigen::Vector2f position = fieldmodel.points[j] - seen_points[i];
            Eigen::Matrix2f check_pos;
            static const Eigen::Vector2f position_error = Eigen::Vector2f(point_position_error, point_position_error);
            check_pos.col(0) = position - position_error;
            check_pos.col(1) = position + position_error;

            check_pos.row(0) = find_overlay(check_pos.row(0), best_pos.row(0));
            check_pos.row(1) = find_overlay(check_pos.row(1), best_pos.row(1));
            //Verify that there is an overlay in possible positions
            if(!(check_pos(0,0) < position(0) - point_position_error || check_pos(1,0) < position(1) - point_position_error ))
            {
                best_pos = check_pos;
                ++matching_count;
            }
        }

    }
    pos = best_pos;
    return point_evaluation_faktor * matching_count;
}

float Line_Matcher::normalize_data(const Line_Samples& line_samples, Line_Samples& projected_samples, int longest_line)
{
    float angle = 0;
    if(longest_line != -1)
    {
        Line& reference = line_samples.lines[longest_line];
        float angle_h = acos(reference.direction.dot(horizontal));//Direction is normalized
            float angle_v = acos(reference.direction.dot(vertikal));//Direction is normalized
        if(fabs(angle_h) < fabs(angle_v))
        {
            angle = angle_h;
        }
        else
        {
            angle = angle_v;
        }
        if((reference.direction.x() > 0.707 && reference.direction.y() < 0)
            || (reference.direction.y() > 0.707 && reference.direction.x() > 0) )//Noch einmal testen
        {
            angle = -angle;
        }
    }
    rotate_samples(line_samples, projected_samples, angle);
    return angle;
}

void Line_Matcher::rotate_samples(const Line_Samples& line_samples, Line_Samples& projected_samples, float angle)
{
    const Eigen::Matrix2f rotate = Location::rotate(angle);//From Utils

    std::vector<Line>& projected_lines = projected_samples.lines;
    projected_lines.clear();
    const std::vector<Line>& lines = line_samples.lines;
    projected_lines.reserve(lines.size());
    foreach(const Line& current, lines)
    {
        projected_lines.push_back(Line(current, rotate));
    }

    std::vector<Circle>& projected_circles = projected_samples.circles;
    projected_circles.clear();
    const std::vector<Circle>& circles = line_samples.circles;
    projected_circles.reserve(circles.size());
    foreach(const Circle& current, circles)
    {
        projected_circles.push_back(Circle(current, rotate));
    }

    std::vector<Eigen::Vector2f>& projected_points = projected_samples.points;
    projected_points.clear();
    const std::vector<Eigen::Vector2f>& points = line_samples.points;
    projected_points.reserve(points.size());
    foreach(const Eigen::Vector2f& current, points)
    {
        projected_points.push_back(rotate * current);
    }
}

int Line_Matcher::get_longest_line(std::vector<Line>& lines)
{
    int index = -1;
    float length = 0;
    for(int i = 0; i < lines.size(); ++i)//find the longest line fragment
    {
        if(lines[i].length > length)
        {
            length = lines[i].length;
            index = i;
        }
    }
    return index;
}

void Line_Matcher::print_debug_shapes(float max_matching_distance, const Line_Samples& line_samples)
{
    m_debug_shapes.clear();

    //IF_DEBUG(3,;) else return; //Cooler hack erst wenn diese funktion keine Logik mehr macht
    const std::vector<Line>& lines = line_samples.lines;
    foreach(const Line& current, lines)
    {
        DEBUG_SHAPES3(pa::line(current.begin, current.end, pa::Cyan));
    }
    const std::vector<Circle>& circles = line_samples.circles;
    foreach(const Circle& current, circles)
    {
        DEBUG_SHAPES3(pa::circle(current.midpoint, current.radius, pa::Cyan));
    }
    const std::vector<Eigen::Vector2f>& points = line_samples.points;
    foreach(const Eigen::Vector2f& current, points)
    {
        DEBUG_SHAPES3(pa::point(current, pa::Cyan));
    }

    for(int i = 0, n = possible_positions.size(); i < n; ++i)
    {
        Matrix3_2f inverted_pos;
        //Evry position has an inverted one with negated coordinates
        inverted_pos.topLeftCorner<2,2>() = - possible_positions[i].topLeftCorner<2,2>();
        //"Rotating" the inverted position by 180°
        inverted_pos.row(2) = possible_positions[i].row(2) + Eigen::Matrix<float, 1, 2>(pi, 0);

        possible_positions.push_back(inverted_pos);
    }
    foreach(const Matrix3_2f& pos, possible_positions)
    {
        if(pos(2,1) > 0.75 * max_matching_distance && pos(2,1) > max_matching_distance - 0.75)//(2,1) contains the matching distance
        {
            pa::Color color = pa::Pink;
            if(pos(2,1) == max_matching_distance) color = pa::Cyan;
            //Making some stuff printing the "new" debug_shape robot
            if((pos.col(0).head<2>() - pos.col(1).head<2>() ).norm() > 0.5)
            {
                DEBUG_SHAPES3(pa::robot(pos.col(0), color));
                Eigen::Vector3f position = pos.col(1);
                position(2) = pos(2,0);
                DEBUG_SHAPES3(pa::robot(position, color));
                //Zwei einzelne Positionen
            }
            else
            {
                Eigen::Vector3f position = pos.col(0);
                position.head<2>() = (position.head<2>() + pos.col(1).head<2>() ) / 2;
                DEBUG_SHAPES3(pa::robot(position, color));
                //Den Mittelwert der Positionen
            }
        }
    }
    DEBUG(4, "Positions", m_debug_shapes);
    DEBUG(4, "DrawDebugShapes", true);
}

