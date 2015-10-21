#ifndef POINTCLOUD_AND_POINTCLOUDPROVIDER_IMPLEMENTATION_HPP__
#define POINTCLOUD_AND_POINTCLOUDPROVIDER_IMPLEMENTATION_HPP__

#include <stdint.h>
#include <cmath>
#include <algorithm>

#include <Eigen/Core>
#include "../../nabo/nabo.h"

#include <array>
#include <memory>

#include "pointcloud.hpp"
#include "common_type_definitions.hpp"

namespace Vision {
namespace MonteCarlo {
using namespace Eigen;
using namespace std;

/**
 * Some small function to modify the distribution of the points.
 * They were extended in septembra 2014 to allow us the use of more custemizable
 * distribution manipulation fuctions @Robert
 */
namespace intern {
    inline double u(double x) {
        return pow(0.9*x + 0.1, x+1.8);
    }

    inline double w(double x) {
        return 1-(x < 0.05 ? x/0.05 * u(0.05) : u(x));
    }

    inline double s(double x, const float vmax=0.5) {
        const static double pi = 3.1415926;
        return x-(sin(pi*2*(x-0.5*vmax + 0.25) + pi) - sin(pi*2*(0.5*vmax - 0.25)))/ (4 * pi);// Vorher: return 0.5*x + (0.5*x - sin(pi*2*x + pi) / (4 * pi));#
    }

    inline Matrix<double, 5, 1> create_pol_parameters(const float vmax, const float m, const float hm) {
        double a = (m - hm/vmax) / vmax,b = hm / vmax - a * vmax,a1=(hm - 1 - (vmax-1)*m)/(2 * vmax - 1 - vmax * vmax),b1=m - 2 * vmax * a1,c1=1-a1-b1;
        return (Matrix<double, 5, 1>()<<a,b,a1,b1,c1).finished();
    }

    inline Vector4d create_exp_parameters(const float vmax, const float m, const float hm, const unsigned itm = 200) {
        double e0 = log((hm + m)/ m) / (-vmax), e1 = log((1 - hm + m) / m) / (1-vmax);
        for(unsigned i = 0; i < itm; ++i) {
            e0 = log((hm + m / abs(e0))/ m * abs(e0)) / (-vmax);
            e1 = log((1 - hm + m / e1) / m * abs(e1)) / (1-vmax);
        }
        return (Vector4d()<<e0, e1,m,hm).finished();
    }

    inline Matrix<double, 9, 1> create_mixed_parameters(const float vmax, const float m, const float hm) {
        return (Matrix<double, 9, 1>()<<create_pol_parameters(vmax, m, hm), create_exp_parameters(vmax, m, hm)).finished();
    }

    inline double pol(const double x, const float vmax, const Matrix<double, 5, 1>& params) {
        return x <= vmax ?
        x * x * params(0) + x * params(1):
        x * x * params(2) + x * params(3) + params(4);
    }

    inline double exp(const double x, const float vmax, const Vector4d& params) {
        const double& m = params(2), &hm = params(3);
        return x <= vmax ?
        hm - m / params(0) + m / params(0) * ::std::exp((x - vmax) * params(0)):
        hm - m / params(1) + m / params(1) * ::std::exp((x - vmax) * params(1));
    }

    inline double mixed(const double x, const float vmax, const Matrix<double, 9, 1>& params, bool pol_after_vmax=true) {
        return x <= vmax ?
        (pol_after_vmax ? exp(x, vmax, params.tail<4>()): pol(x, vmax, params.head<5>())):
        (pol_after_vmax ? pol(x, vmax, params.head<5>()): exp(x, vmax, params.tail<4>()));
    }

    /*
     * A example to plot the old sinusodial function and the two new ones using bash and gnuplot:
     * for i in {1..9}; do gnuplot --persist <<< "vmax=0.$i;m=0.5;hm=vmax;itm=200;pi=3.14159265358;set yrange[0:1];e0 = log((hm + m)/ m) / (-vmax); e1 = log((1 - hm + m) / m) / (1-vmax);do for [i=1:itm]{e0 = log((hm + m / abs(e0))/ m * abs(e0)) / (-vmax); e1 = log((1 - hm + m / e1) / m * abs(e1)) / (1-vmax)};a = (m - hm/vmax) / vmax;b = hm / vmax - a * vmax;a1=(hm - 1 - (vmax-1)*m)/(2 * vmax - 1 - vmax * vmax);b1=m - 2 * vmax * a1;c1=1-a1-b1;exp1(x) =  hm - m / e1 + m / e1 * exp((x - vmax) * e1);exp0(x) = hm - m / e0 + m / e0 * exp((x - vmax) * e0);pol0(x) = a * x * x + b * x;pol1(x) = a1 * x * x + b1 * x + c1;old(x)=x-(sin(pi*2*(x-0.5*vmax + 0.25) + pi) - sin(pi*2*(0.5*vmax - 0.25)))/ (4 * pi); plot [0:1] exp0(x) * (x < vmax) +  exp1(x) * (x >= vmax), pol0(x) * (x < vmax) + pol1(x) * (x >= vmax),old(x)" ; done
     */
}

/**
 * Generates random points in the clouds array, sorts the points and replaces the points in the array.
 */
template<>
void Cloud::generate_random_points(MatrixXf& matrix, const float vmax, const float offset) const {
    std::array<int, Cloud::n> numbers;
    // Define deafult pointcloud density function if not set otherwise
    #ifndef FUNC
        #define FUNC mixed
    #endif
    #define FUNCTION(FUNC) intern::create_ ## FUNC ## _parameters
    #define REVERSE_PARAMETER(A,B) B(A)
    #define PARAMETER_FUNCTION REVERSE_PARAMETER(FUNC, FUNCTION)
    const float m = 0.6;
    auto parameters = PARAMETER_FUNCTION (vmax, m, vmax + offset);
    for(int i = 0; i < Cloud::n; i++) {
        double rx = rand() / (double(RAND_MAX) + 1);
        double ry = rand() / (double(RAND_MAX) + 1);

        // transform points, we don't want to have a uniform distribution
        //ry = intern::s(ry, vmax);
        ry = intern::FUNC(ry, vmax, parameters);

        numbers[i] = static_cast<int>((ry*(height-1)) * width + (rx*width));
    }

    // Sort
    sort(numbers.begin(), numbers.end());

    // Insert in point matrix
    matrix.resize(2, Cloud::n);
    for(int i = 0; i < Cloud::n; i++)
        matrix.col(i) << numbers[i]%width, numbers[i]/width;
}

/**
 * Creates a new pointcloud.
 * First genereates points, sorts them and links them at least.
 */
template<>
Cloud::PointCloud(const int width, const int height, float vmax, float offset) {
    this->width = width;
    this->height = height;

    // create Points
    MatrixXf points;
    this->generate_random_points(points, vmax, offset);

    // Create KD Tree
    std::shared_ptr<Nabo::NNSearchF> nns(
        Nabo::NNSearchF::createKDTreeLinearHeap(points));

    // Perform nearest neighbour search
    MatrixXi indices(static_cast<int>(Cloud::k), static_cast<int>(Cloud::n));
    MatrixXf dists2(static_cast<int>(Cloud::k), static_cast<int>(Cloud::n));
    nns->knn(points, indices, dists2, Cloud::k);

    // Remember all nearest numbers
    for(int i = 0; i < Cloud::n; i++) {
        // Altes Objekt zerstören, sauber ist sauber.
        cloud[i].~PointType();

        // Konstruktor mit dem placement-new aufrufen
        new(&cloud[i]) PointType(points.col(i).cast<int>());
        for(int j = 0; j < Cloud::k && !isinf(dists2(j,i)); j++)
            cloud[i].add_nn_index(indices(j,i), sqrt(dists2(j,i)));
    }
}

using std::promise;
using std::shared_ptr;
using std::shared_future;
using std::make_shared;

template<class CloudType>
struct ThreadWorker {
    void operator()(typename PointCloudProvider<CloudType>::Promises promises, float vmax, int height, int width, float offset);
};

template<>
void ThreadWorker<Cloud>::operator()(typename PointCloudProvider<Cloud>::Promises promises, float vmax, int height, int width, float offset) {
    Debug::Scope m_debug("PointCloudProvider.Worker");

    for(unsigned i = 0; i < promises.size(); i++) {
        DEBUG_LOG(INFO, "Create Pointcloud #" << (i+1) << "Max density point: " <<vmax);

        shared_ptr<Cloud> cloud(new Cloud(width, height, vmax, offset));
        promises[i]->set_value(cloud);
    }

    DEBUG_LOG(IMPORTANT, "All PointClouds created.");
}

template<>
PointCloudProvider<Cloud>::PointCloudProvider(int width, int height, int count, float vmax, float offset)
: futures(count) {

    Promises promises(count);
    for(unsigned i = 0; i < promises.size(); i++) {
        promises[i] = make_shared<promise<SharedCloudType> >();
        futures[i] = promises[i]->get_future();
    }

    IF_DEBUG(INFO,Debug::Scope("PointCloudProvider") << "Start Thread");
    thread = std::thread(ThreadWorker<Cloud>(), promises, vmax, height, width, offset);
}

template<>
PointCloudProvider<Cloud>::~PointCloudProvider() {
    thread.join();
}

template<>
const Cloud& PointCloudProvider<Cloud>::get() {
    int cloud_index = rand() % futures.size();
    while(cloud_index != 0 && !futures[cloud_index].valid())
        cloud_index = rand() % cloud_index;

    // Punktwolke holen
    return *futures[cloud_index].get();
}

} } //namespace

#endif
