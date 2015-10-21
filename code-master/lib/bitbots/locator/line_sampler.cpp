#include <boost/foreach.hpp>
#include <Eigen/Core>
#include <utility>

#include "../vision/sample.hpp"
#include "line_sampler.hpp"
#include "../debug/debug.hpp"
#include "image_point_to_location_transformer.hpp"

#define foreach BOOST_FOREACH

using namespace Location;
using Vision::Sample::LineSample;

//static Debug::Scope debug("Locator");//Locator //muss vlt noch so getweak werden wie der Locator, böse ins Visiondebug hinein

static const Eigen::Vector4f ORIGIN(0, 0, 0, 1);
static const Eigen::Vector4f X_AXIS(1, 0, 0, 0);
static const Eigen::Vector4f Y_AXIS(0, 1, 0, 0);


void Line_Sampler::update(const std::vector<LineSample>& line_points)
{
	m_debug_shapes.clear();
	points.clear();
	lines.clear();
	circles.clear();
	if(line_points.size() < 30)
	{
		return;
	}
	init_point_locations();
	std::vector<int> cluster_begin_indices;
	project_points(line_points, cluster_begin_indices);//Pojeziere Punkte und sammle die Clusterindizes
	std::vector<char> visited(projected.size(), 0);

	//For every Cluster, which is specfied by begin and end index, do something
	std::vector<Eigen::Vector2f> cogs;
	for(int current_cluster = cluster_begin_indices.size() - 2; current_cluster >= 0; current_cluster--)
	{
		for(int i = cluster_begin_indices[current_cluster+1] -1; i >= cluster_begin_indices[current_cluster]; --i)
		{
			if(visited[i])
			{
				continue;
			}
			int cluster_length = cluster_begin_indices[current_cluster+1] - cluster_begin_indices[current_cluster];
			int length = std::min( ((int)(0.75 * sqrt(cluster_length) )), 3);
			chain_cog(i, length, cogs, visited, current_cluster);
		}
	}
	check_structure(cogs);
	find_lonely_point(cluster_begin_indices);

    //Just a test run
    //is not stable enough to be executed normally
    //improve_sample_quality();

    print_debug_shape_orientation();
	//std::cout<< "Update complete" <<std::endl;

}

void Line_Sampler::improve_sample_quality()
{
    if(lines.size() > 4)
    {
        find_parallel_lines();
    }
    if(circles.size() != 0)
    {
        handle_circles();
    }
    if(points.size() != 0)
    {
        handle_points();
    }
}

void Line_Sampler::handle_circles()
{
    for(int i = 1; i < circles.size(); ++i)
    {
        const Circle& circle = circles[i];
        std::vector<int> possible_false_lines;
        bool is_valid;
        for(int j = 0; j < lines.size(); ++j)
        {
            Line& line = lines[i];
            if(line.length < 0.15 * circle.radius
             && abs((line.begin - circle.midpoint).norm() - circle.radius) < 0.15 * circle.radius
             && abs((line.begin - circle.midpoint).norm() - circle.radius) < 0.15 * circle.radius
             && !(is_low_angle(line.begin - circle.midpoint, line.direction, 0) || is_low_angle(circle.midpoint - line.begin, line.direction, 0)))
            {
                possible_false_lines.push_back(i);
            }
            else if(is_low_angle(line.begin - circle.midpoint, line.direction, 0) || is_low_angle(circle.midpoint - line.begin, line.direction, 0))
            {
                is_valid = true;
            }
        }
        if((is_valid && !possible_false_lines.empty())|| possible_false_lines.size() > 2)
        {
            //possible_false_lines mustn't be empty
            for(int n = 0, j = possible_false_lines[n]; j < lines.size(); ++j)
            {
                if(j > possible_false_lines[n] && n < possible_false_lines.size() - 1)
                {
                    ++n;
                }
                if(j + n + 1< lines.size())
                {
                    //destroying the old Object, not necessary with Lines but more robust
                    lines[j].~Line();
                    lines[j] = lines[j + n + 1];
                }
                else
                {
                    lines.pop_back();
                    --j;
                }
            }
        }
    }
    //std::cout<<"Improved circles"<<std::endl;
}

void Line_Sampler::handle_points()
{
    for(int i = 0; i < points.size(); ++i)
    {
        foreach(const Line& line, lines)
        {
            if(is_low_angle(line.begin - points[i], line.direction) || is_low_angle(line.begin - points[i], line.direction))
            {
                points[i].~Matrix<float,2,1>();
                points[i] = points[points.size() - 1];
                points.pop_back();
            }
        }
    }
}

void Line_Sampler::find_parallel_lines()
{
    std::vector<bool>visited(lines.size(), false);
    std::vector<std::vector<Line> > parallel_lines;
    //building components out of parallel lines
    for(int i = 0; i < lines.size(); ++i)
    {
        if(visited[i])
        {
            continue;
        }
        visited[i] = true;//Can be ignored, when I do this clever
        const Line& sample = lines[i];
        //Filtering out to long lines, or those that are to far away
        if(sample.length > 6 || abs(sample.begin.x()) > 6 || abs(sample.begin.y()) > 6
                || abs(sample.end.x()) > 6 || abs(sample.end.y()) > 6)
        {
            continue;
        }
        parallel_lines.push_back(std::vector<Line>());
        std::vector<Line>& parallel_component = parallel_lines[parallel_lines.size() - 1];
        parallel_component.push_back(sample);
        for(int j = lines.size() - 1; j > i; --j)
        {
            //What is with too long lines and those that are to far away?
            if(!visited[j] && is_low_angle_normed(sample.direction, lines[j].direction, 0))
            {
                visited[j] = true;
                parallel_component.push_back(lines[j]);
            }
        }
    }
    std::vector<float> lengths(parallel_lines.size(), 0);
    //improving quality of the parallel components
    for(int i = 0; i < parallel_lines.size(); ++i)
    {
        std::vector<Line>& parallel_component = parallel_lines[i];
        float length = 0;
        int j = 1;
        for(; j < parallel_component.size(); ++j)
        {
            for(int n = j; n < parallel_component.size(); ++n)
            {
                const Line& first = lines[j - 1];
                const Line& second = lines[n];
                Eigen::Matrix2f A;
                //turn the first direction by 90°
                A.col(0) << first.direction.y(), - first.direction.x();
                A.col(1) = second.direction;
                Eigen::Vector2f uv = A.householderQr().solve(first.begin - second.begin);
                //The first value of uv represents the "minimal" distance between the two lines where they perfectly parallel
                //The second one is the distance between the two beginning points, when the lines were on a straight line
                if(abs(uv(0)) < 0.2)
                {
                    //Not so good, when Line were a complex type with a destructor.
                    parallel_component[j - 1] = sum_up_lines(parallel_component[j - 1], parallel_component[n], uv(1));
                    //deleting line n by overriding it with the last line and popping it; Line doens't have a destructor
                    // otherwise the n'th line should be destructed
                    if(n < parallel_component.size() - 1)
                    {
                        parallel_component[n].~Line();
                    }
                    parallel_component[n] = parallel_component[parallel_component.size() - 1];
                    parallel_component.pop_back();
                }
            }
            length += parallel_component[j - 1].length;
        }
        if(j != parallel_component.size() - 1)
        {
            length += parallel_component[j - 1].length;
        }
        lengths[i] = length;
    }
    //lines.clear();
    if(parallel_lines.size() > 1)
    {
        lines.clear();
        int index_longest_component = 0, index_longest_component_but_one = -1;
        for(int i = 1; i < lengths.size(); ++i)
        {
            if(lengths[i] >= lengths[index_longest_component])
            {
                index_longest_component_but_one = index_longest_component;
                index_longest_component = i;
            }
            else if(lengths[i] > lengths[index_longest_component_but_one])
            {
                index_longest_component_but_one = i;
            }
        }
        const std::vector<Line>& longest = parallel_lines[index_longest_component];
        foreach(const Line& line, longest)
        {
            lines.push_back(line);
        }
        const std::vector<Line>& longest_but_one = parallel_lines[index_longest_component_but_one];
        foreach(const Line& line, longest_but_one)
        {
            lines.push_back(line);
        }
    }
    //std::cout<<"Improved lines"<<std::endl;
    //else
    //{
    //    for(int i = 0; i < parallel_lines.size(); ++i)
    //    {
    //        std::vector<Line>& l = parallel_lines[i];
    //        for(int j = 0; j < l.size(); ++j)
    //        {
    //            lines.push_back(l[j]);
    //        }
    //    }
    //}
}

Line Line_Sampler::sum_up_lines(const Line& first, const Line& second, float v)
{
    const Eigen::Vector2f& begin = v < 0? first.begin: second.begin;
    const Eigen::Vector2f& end = first.length + v < second.length? first.end: second.end;
    return Line(begin, end);
}

void Line_Sampler::find_lonely_point(const std::vector<int>& cluster_begin_indices)
{
	std::vector<int> lonely_poins;
	for(int i = 0; i < 25; ++i)
	{
		for(int j = 0; j < 25; ++j)
		{
			if(point_locations[i][j] > 0)
			{
				bool valid = true;
				for(int k = i - 1; k < i + 2; ++k)
				{
					for(int l = j - 1; l < j + 2; ++l)
					{
						if(k>=0&&l>=0&&k<25&&l<25&&(k!=i||l!=j)&&point_locations[k][l] != 0)
						{
							valid = false;
							break;
						}
					}
				}
				if(valid)
				{
					lonely_poins.push_back(point_locations[i][j] - 1);
				}
			}
		}
	}
	for(int i = 0; i < lonely_poins.size(); ++i)
	{
		DEBUG_SHAPES4(pa::circle(
			project_vector_for_debug(
				projected[cluster_begin_indices[lonely_poins[i]+1]-1]),5,pa::Blue));
		points.push_back(Eigen::Vector2f(projected[cluster_begin_indices[lonely_poins[i]+1]-1]) );
	}
}

void Line_Sampler::mark_location(const Eigen::Vector2f& point, const int index)
    {//x is the distance to the robot -> direction in front of
		int x = point.x() * 4;//x > 0
		int y = point.y() * 4 + 12;
		if(x >= 0 && y >= 0 && x < 25 && y < 25)
		{
			if(point_locations[x][y] == 0)
			{
				point_locations[x][y] = index + 1;
			}else if(point_locations[x][y] != index + 1)
			{
				point_locations[x][y] = -1;
			}//when the cluster index is alredy the marked index, do nothing
		}
	}

/*
 * Checks the structure of the given centers of gravities
 * Will find out wheather they are in line over edge or in a circle
 * Requires a minimum size of 5
 */
bool Line_Sampler::check_structure(const std::vector<Eigen::Vector2f>& cogs, bool recursive_call)
{
	if(cogs.size() < 5)
	{
		return false;
	}
	//std::cout<<"Checking Structure"<<std::endl;
	std::vector<Eigen::Vector2f> interruption_points;
	interruption_points.push_back(cogs[0]);
	bool found_something = false;
	int index = 0;
	while(index < cogs.size())
	{
		int begin_index = index;
		bool valid = true;
		//Eigen::Vector2f mean_direction = cogs[begin_index + 1] - cogs[begin_index];
		while(valid && index < cogs.size() - 2)
		{//Compares the direction from last newest but two point with the mean direction//When they're similar -> continue
			Eigen::Vector2f direction = cogs[index + 2] - cogs[(index + begin_index) / 2 + 1];//Doch begin_index statt index + 1?
			Eigen::Vector2f approval = cogs[(index + begin_index) / 2 + 1] - cogs[begin_index];
            valid = is_low_angle(approval, direction, index - begin_index);
			++index;
		}
        if(valid)
        {
            ++index;
        }
        Eigen::Vector2f mean_direction = cogs[index] - cogs[begin_index];
		//Structure is long enough and the components are relativly close to each other
		if(index - begin_index > 1 && (index - begin_index > 10 || (mean_direction.norm() / (index - begin_index - 1)) < 0.15) )
		{//Mal was Testen -> sehen was davon erkannt wird
			DEBUG_SHAPES4(pa::line(project_vector_for_debug(cogs[begin_index]),project_vector_for_debug(cogs[begin_index] + mean_direction), pa::Cyan));//Gebe Line in die DebugView
			Eigen::Vector2f begin = cogs[begin_index], end = cogs[begin_index] + mean_direction;
			lines.push_back( (mean_direction.x()< -0.707 || mean_direction.y() < -0.707) ?
			Line(end, begin, -mean_direction) :
			Line(begin, end, mean_direction) );
			//Now the direction is "from left to right" or upwards
			found_something = true;
		}
		if(index < cogs.size() - 1)
		{
			interruption_points.push_back(cogs[index+1]);//marking as a possible round component
		}
	}
	//When called rekursive, I don't expect more information of checking a circle a second time
	if(interruption_points.size() > 4)
	{//find out wheather it can be a circle
		//std::cout<<"Checking circle"<< std::endl;
        //Checking circle here
        found_something = check_circle(interruption_points);
	}//call one time rekursive, when no strukture was found, only call rekursive, when having more than 5 points
	//I think there are situations, so calling recursive once can improve results
	return found_something || recursive_call ? found_something:
		interruption_points.size() > 4 ?check_structure(interruption_points, true) : false;
}

/*
 * Calculate multiple centers of gravity of a given length an mark the used points as visited
 */
void Line_Sampler::chain_cog(int index, const int length, std::vector<Eigen::Vector2f>& cogs, std::vector<char>& visited, const int marking_index)
{
	while(projected[index].get_parent() != index)
	{
		VectIndex v = cog(index,length, visited);//Calculate a small center of gravity
		cogs.push_back(v.first);
		index = v.second;
		mark_location(v.first, marking_index);
		if(visited[index])
		{
			break;// cancel when found an visited point
		}
	}
}

/*
 * Calculate the center of gravity to a given point using its parent, parent's parent and so on
 * Maximum is the given length, return also the last used index
 */
VectIndex Line_Sampler::cog(int index, const int length, std::vector<char>& visited)
{
	Eigen::Vector2f cog(0,0);
	int i= 0;
	for(; i < length; ++i)
	{
		cog = cog + projected[index];
		visited[index] = 1;
		if(projected[index].get_parent() == index)//Using parent structure
		{
			++i;
			break;
		}else
		{
			index = projected[index].get_parent();
		}
	}
	cog /= (i);
	return VectIndex(cog, index);
}

/*
 * Projects a Vector, so that you can print for debug.
 * Returns the Vector.
 */
Eigen::Vector2f Line_Sampler::project_vector_for_debug(const Eigen::Vector2f& v)
{
	return Eigen::Vector2f(150 + v.x()*100, 300 - v.y()*100);
}

/*
 * Check wheather some given points can lay on a circle
 * Calculate possible midpoints of that circle and validate the results
 *
 */
bool Line_Sampler::check_circle(const std::vector<Eigen::Vector2f>& circle_points)
{
	if(circle_points.size() < 5)
	{
		return false;
	}
	std::vector<Eigen::Vector2f> midpoints;
    std::vector<float> distances;

	for(int i = 0; i < circle_points.size()-2; ++i)
	{//Calculate a possible midpoint usin triangle calculations
		//Let the first point be a, the second point b and the third point c
		Eigen::Vector2f ac = circle_points[i+2] - circle_points[i];
		Eigen::Vector2f bc = circle_points[i+2] - circle_points[i+1];
		Eigen::Vector2f ac_midpoint_direction(-ac.y(), ac.x());
		Eigen::Vector2f ac_midpoint = circle_points[i] + ac / 2;
		Eigen::Matrix2f equation;
		equation.col(0) << ac_midpoint_direction;
		equation.col(1) << Eigen::Vector2f(-bc.y(), bc.x());
		Eigen::Vector2f abc = equation.householderQr().solve((circle_points[i+1] + bc / 2) - ac_midpoint);
		Eigen::Vector2f midpoint = ac_midpoint + abc.x() * ac_midpoint_direction;

        float distance = (midpoint - circle_points[i]).norm();
		if(distance < 0.9 && distance > 0.3)//Maximum radius//Feldradius 0.6
		{
            distances.push_back(distance);
			midpoints.push_back(midpoint);
		}
	}
	//For each midpoint, calculate the number of points which have quiet the same distance
	Eigen::ArrayXi valid_count = Eigen::ArrayXi::Zero(midpoints.size());
	int max_count = 0;
    int best_index = -1;
	for(int i = 0; i < midpoints.size(); ++i)
	{
		DEBUG_SHAPES4(pa::point(project_vector_for_debug(midpoints[i]),pa::Pink));
		float mean_distance = distances[i];
		foreach(const Eigen::Vector2f& circle_point, circle_points)
		{
			if(abs(mean_distance - (midpoints[i] - circle_point).norm()) < 0.09375 * mean_distance)
			{//Whean the error is less than 10%
				valid_count(i)= valid_count(i) + 1;
				if(valid_count(i) > max_count)
				{
					max_count = valid_count(i);
                    best_index = i;
				}
			}
		}
	}
	//std::cout<<"Max " << max_count << std::endl;
	if(max_count < 5)//Not enough valid points
	{
		return false;
	}
	else
	{
        Eigen::Vector2f midpoint = midpoints[best_index];
        float distance = distances[best_index];
		DEBUG_SHAPES4(pa::circle(project_vector_for_debug(midpoint), 100*distance, pa::Green));
		circles.push_back(Circle(midpoint, distance));
		return true;
	}
}


/*
 * Overload function, projects Points and counts the number of the clusters
 * Return a vector containing the begin indices of the clusters
 */
void Line_Sampler::project_points(const std::vector<LineSample>& line_points, std::vector<int>& cluster_begin_indices)
{
    this->projected.clear();

    int index = 0;
    foreach(const LineSample& point, line_points) {

        const Eigen::Vector2f location = transformer.transform_point(point);

        // Merken
        this->projected.push_back(LineSample(Vision::Sample::ColorSample(location, point.get_index()),point.get_parent()) );
        if(point.get_parent() >= this->projected.size() || point.get_parent() < 0)
        {
			std::cout<<"Irgendetwas lief hier gewaltig schief; Index: " << point.get_parent() << "local size " << this->projected.size() <<std::endl;
		}
		if(point.get_parent() == index)
		{
			cluster_begin_indices.push_back(index);
		}

        // Zeichnen
        DEBUG_SHAPES4(pa::dot(project_vector_for_debug(location), pa::Yellow));
        ++index;
    }
    cluster_begin_indices.push_back(index);//Add the length to make it possible to calculate the length od the last cluster
}

void Line_Sampler::print_debug_shape_orientation()
{
    #if 1
    foreach(const Circle& circle, circles)
    {
		DEBUG_SHAPES4(pa::circle(project_vector_for_debug(circle.midpoint), 100*circle.radius, pa::Red));
    }
    foreach(const Line& line, lines)
    {
        DEBUG_SHAPES4(pa::line(project_vector_for_debug(line.begin),project_vector_for_debug(line.end), pa::Red));
    }
    #endif

    //Place the imaginary robot for orientation when looking at projected points
	DEBUG_SHAPES4(pa::line(150, 300, 250, 250, pa::Green));
    DEBUG_SHAPES4(pa::line(150, 300, 250, 350, pa::Green));
    DEBUG_SHAPES4(pa::point(150, 300, pa::Green).describe("Robot"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(0,1)), pa::Green));//Some validation
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(0,1)), pa::Green).describe("1 m"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(0,2)), pa::Green).describe("2 m"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(0,2)), pa::Green));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(0,3)), pa::Green).describe("3 m"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(0,3)), pa::Green));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(1,0)), pa::Green));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(1,0)), pa::Green).describe("1 m"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(2,0)), pa::Green).describe("2 m"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(2,0)), pa::Green));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(3,0)), pa::Green).describe("3 m"));
    DEBUG_SHAPES4(pa::point(project_vector_for_debug(Eigen::Vector2f(3,0)), pa::Green));
}

