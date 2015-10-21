#include "fitcircle.hpp"

/**
    Kreis an die Punkte (2xN-Array) anfitten.
*/
Eigen::Vector3f fit_circle(const Eigen::Array2Xf& points) {
    Eigen::Array2f mean = points.rowwise().mean();
    Eigen::Array2Xf uv(points.colwise() - mean);
    
    Eigen::Array2f Sp2 = uv.square().rowwise().sum();
    Eigen::Array2f Sp3 = uv.cube().rowwise().sum();
    
    float Suv = (uv.row(0) * uv.row(1)).sum();
    float Suvv = (uv.row(0) * uv.row(1).square()).sum();
    float Svuu = (uv.row(0).square() * uv.row(1)).sum();
    
    // Rechte Seite berechnen
    Eigen::Vector2f b((Sp3 + Eigen::Array2f(Suvv, Svuu)) / 2);
    
    // Linke Seite berechnen
    Eigen::Matrix2f A;
    A << Sp2(0), Suv, Suv, Sp2(1);
    
    // Gleichungssystem Lösen
    Eigen::Array2f mid = A.inverse() * b;
    
    // Quadrat des Radius berechnen
    float radius = sqrt(mid.square().sum() + Sp2.sum() / points.cols());
    return (Eigen::Vector3f() << (mid + mean), radius).finished();
}

