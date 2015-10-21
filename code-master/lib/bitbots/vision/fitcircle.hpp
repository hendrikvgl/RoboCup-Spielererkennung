#ifndef __FITCIRCLE_H__
#define __FITCIRCLE_H__

#include <Eigen/Core>
#include <Eigen/Geometry>

/**
    Gibt Mittelpunkt und Radius eines Kreises zurück, der die
    Punkte in "points" mit dem minimalen quadratischen Fehler
    anfittet.
*/
Eigen::Vector3f fit_circle(const Eigen::Array2Xf& points);

#endif /* __FITCIRCLE_H__ */

