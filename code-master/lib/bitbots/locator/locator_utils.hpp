#ifndef _LOCATOR_UTILS_HPP
#define _LOCATOR_UTILS_HPP

#include <Eigen/Core>

namespace Location{
/**
 * Returns a rotation Matrix
 */
inline
const Eigen::Matrix2f rotate(const float angle)
{
    Eigen::Matrix2f result;
    result << cos(angle), sin(angle),
             -sin(angle), cos(angle);
    return result;
}

//namespace
}

#endif
