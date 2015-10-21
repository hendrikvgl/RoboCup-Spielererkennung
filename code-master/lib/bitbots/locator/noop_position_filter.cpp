#include "noop_position_filter.hpp"
#include <cmath>
#include <boost/foreach.hpp>
#include <Eigen/Core>
#include "locator_utils.hpp"
#define foreach BOOST_FOREACH

using namespace Location;
static const float overlay_tolerance = 0.5;

void Noob_Position_Filter::filter_impossible_positions(std::vector<Position >& suggestions)
{
    for(int i = 0; i < suggestions.size(); ++i)
    {
        Position& position = suggestions[i];
        //x position in row 0
        position(0,0) = std::max(std::min(position(0,0), position(0,1)), (float)-3.7);
        position(0,1) = std::min(std::max(position(0,0), position(0,1)), (float)3.7);
        //y position in row 1
        position(1,0) = std::max(std::min(position(1,0), position(1,1)), (float)-2.7);
        position(1,1) = std::min(std::max(position(1,0), position(1,1)), (float)2.7);

        bool invalid = position(0,0) == 3.7 || position(0,1) == -3.7
                || position(1,0) == 2.7 || position(1,1) == -2.7;

        //When there is no information, no overlay should be false, otherwise true
        bool no_overlay = position_information.size() > 0;
        if(!invalid)
        {
            foreach(const Eigen::Matrix2f& info, position_information)
            {
                Eigen::Matrix2f overlay;
                overlay.row(0) = find_overlay(info.row(0), position.row(0) + Eigen::Matrix<float, 1, 2>(-way_moved(0), -way_moved(0)));
                overlay.row(1) = find_overlay(info.row(1), position.row(1) + Eigen::Matrix<float, 1, 2>(-way_moved(1), -way_moved(1)));
                if( overlay(0,0) >= info(0,0) - overlay_tolerance &&
                    overlay(1,0) >= info(1,0) - overlay_tolerance )
                {
                    no_overlay = false;
                    break;
                }
            }
        }

        if(invalid || no_overlay)
        {
            //destroying the old object, although I think it's not necessary
            position.~Matrix<float, 3, 2>();
            position = suggestions[suggestions.size() - 1];
            suggestions.pop_back();
        }
    }
}

void Noob_Position_Filter::update_positions(Eigen::Vector3f& movement, float position_decreasing_factor)
{
    update_information(movement.head<2>());
    foreach(Position& pos, positions)
    {
        Eigen::Vector3f mov;
        mov.head<2>() = rotate(movement(2)) * movement.head<2>();
        mov(2) = movement(2);
        pos.col(0) += mov;
        pos.col(1).head<2>() += mov.head<2>();
        pos(2,1) *= position_decreasing_factor;
    }
}

void Noob_Position_Filter::update_information(Eigen::Vector2f movement)
{
    return;
    float m = std::max(movement(0), movement(1));
    movement<< m,m;
    for(int i = 0; 0 < position_information.size(); ++i)
    {
        Eigen::Matrix2f& area = position_information[i];
        area.col(0) = area.col(0) + movement;
        area.col(1) = area.col(1) - movement;
        if((float)(area(0,1) - area(0,0)) >= 6 || ((float)area(1,1) - area(1,0)) >= 4)
        {
            //area is to large
            position_information[i].~Matrix<float, 2, 2>();
            position_information[i] = position_information[position_information.size() - 1];
            position_information.pop_back();
        }
    }
}

inline
void Noob_Position_Filter::update_global_movement(Eigen::Vector3f& movement)
{
    way_moved.head<2>() += rotate(movement(2)) * movement.head<2>();
    way_moved(2) += movement(2);
}

void Noob_Position_Filter::update(const std::vector<Position >& position_suggestions, Eigen::Vector3f movement)
{
    std::vector<Position > suggestions(position_suggestions);
    update_global_movement(movement);
    filter_impossible_positions(suggestions);
    float pos_factor = suggestions.size() == 0? 1: position_decreasing_factor;
    update_positions(movement, pos_factor);
    filter_impossible_positions(positions);
    match(suggestions);
    set_position();
    DEBUG(3,"Num Positions", positions.size());
    DEBUG(3,"CurrentValue", current_position(2,1));
    //std::cout<<position_suggestions.size() <<" Vorschläge input "<< positions.size()<< " output" << std::endl;
}

void Noob_Position_Filter::set_position()
{
    if(positions.empty())
    {
        return;
    }
    float max_lentgh = 0;
    int index_best_pos = 0;
    for(int i = 0; i < positions.size(); ++i)
    {
        if(positions[i](2,1) > max_lentgh)
        {
            max_lentgh = positions[i](2,1);
            index_best_pos = i;
        }
    }
    current_position = positions[index_best_pos];
    for(int i = 0; i < positions.size(); ++i)
    {
        bool valid = positions[i](2,1) > max_lentgh - 1 || positions[i](2,1) > max_lentgh * 0.75 ;
        if(!valid)
        {
            positions[i].~Matrix<float, 3, 2>();
            positions[i] = positions[positions.size() - 1];
            positions.pop_back();
            if(index_best_pos == positions.size())
            {
                index_best_pos = i;
            }
        }
    }
    //std::cout<< "Best Pos " << index_best_pos <<std::endl;
}

void Noob_Position_Filter::match(const std::vector<Position >& suggestions)
{
    foreach(const Position& sug, suggestions)
    {
        bool valid = false;
        foreach(Position& pos, positions)
        {

            Eigen::Matrix2f overlay;
            overlay.row(0) << find_overlay(sug.row(0), pos.row(0));
            overlay.row(1) << find_overlay(sug.row(1), pos.row(1));
            if(overlay(0,0) < sug(0,0) - overlay_tolerance || overlay(1,0) < sug(1,0) - overlay_tolerance)
            {//no overlay
                continue;
            }
            else
            {
                pos.topLeftCorner<2,2>() = overlay;
                pos(2,1) += sug(2,1);
                valid = true;
                break;
            }
        }
        if(!valid)
        {
            positions.push_back(sug);
        }
    }
}



Eigen::Matrix<float, 1, 2> Noob_Position_Filter::find_overlay(const Eigen::Matrix<float, 1, 2>& org_pos, const Eigen::Matrix<float, 1, 2>& pos)
{
	float begin = org_pos(0) > pos(0)? org_pos(0): pos(0);//Using max
	float end = org_pos(1) < pos(1)? org_pos(1): pos(1);//Using min
	if(begin < end + overlay_tolerance)//Allow a little mistake
	{
		return Eigen::Matrix<float, 1, 2> (std::min(begin,end), std::max(begin,end));
	}
	else
	{
		return Eigen::Matrix<float, 1, 2>(org_pos(0)-1, org_pos(1)-1);
	}
}
