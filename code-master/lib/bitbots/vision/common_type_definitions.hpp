#ifndef _VISION_COMMON_TYPE_DEFINITIONS_HPP__
#define _VISION_COMMON_TYPE_DEFINITIONS_HPP__

#include "sample.hpp"

//Forward declarations for the typedefs to avoid the inclusion.
namespace Vision {
namespace MonteCarlo {
template<int N, int K>
class PointCloud;
}
}

typedef ::Vision::MonteCarlo::PointCloud<55000, 12> Cloud;
/*Beim Anpassen des Sampletyps für das LineCustering, auch die Initailisierung in der RobotVision im filter_samples anpassen*/
typedef ::Vision::Sample::VisionSample LineClusteringSampleType;
static const bool line_clustering_uses_distances = false;
#endif
