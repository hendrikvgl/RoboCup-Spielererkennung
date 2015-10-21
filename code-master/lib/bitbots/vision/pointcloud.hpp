#ifndef _POINT_CLOUD_HPP
#define _POINT_CLOUD_HPP

#include <stdint.h>
#include <algorithm>

#include <memory>
#include <Eigen/Core>
#include "../../nabo/nabo.h"

#include <array>
#include <thread>
#include <future>
#include <boost/utility.hpp>

#include "../debug/debug.hpp"
#include "../debug/debugmacro.h"

namespace Vision {
namespace MonteCarlo {

/**
 * This is a point, used by the Pointcloud.
 * A Point is represented by its position as a vector and the index inside the cloud's point array.
 * Furthermore a Point can hold some neigbours, without checking, they are the neearest ones.
 */
template<int N, class Index> class Point {
private:
    // nn bedeutet nearest neighbour
    int nn_count;
    Eigen::Vector2i pos;
    std::array<Index, N> nn_indices;
    std::array<uint8_t,N> nn_distances;

public:
    Point() : nn_count(0) {}

    Point(const Eigen::Vector2i& pos) : nn_count(0), pos(pos) {
    }

    int get_nn_count() const {
        return nn_count;
    }

    /**
     * Returns the Pointcloud index of the n'th nearest neighbour
     */
    Index get_nn_index(int nr) const {
        assert(nr >= 0 && nr < nn_count);
        return nn_indices[nr];
    }

    /**
     * Returns the distance to the nr'th nearest naighbour
     */
    float get_nn_distance(int nr) const {
        assert(nr >= 0 && nr < nn_count);
        return nn_distances[nr];
    }

    /**
     * Adds a new neighbour
     */
    void add_nn_index(Index idx, float distance) {
        assert(nn_count < N);

        nn_indices[nn_count] = idx;
        nn_distances[nn_count] = (uint8_t)std::min(distance, 255.f);
        ++nn_count;
    }

    const Eigen::Vector2i& get_position() const {
        return pos;
    }

    typedef typename std::array<Index, N>::const_iterator const_iterator;

    const_iterator begin() const {
        return nn_indices.begin();
    }

    const_iterator end() const {
        return nn_indices.begin() + nn_count;
    }
};

using std::promise;
using std::shared_ptr;
using std::shared_future;

/**
 * \brief The container for our pointclouds
 *
 * We use this self written container to provide our pointclouds.
 * Due to large complexity of the creation, this provider starts threads to
 * create the requested amount of pointclouds and returns.
 * Internally this provides uses shared futures and shared promises to store the pointclouds.
 * There is no index bases access on the clouds. A request to any cloud results in a randomly
 * chosen cloud.
 */
template<class CloudType>
class PointCloudProvider : boost::noncopyable {
public:
    typedef shared_ptr<CloudType> SharedCloudType;
    typedef std::vector<shared_future<SharedCloudType> > Futures;
    typedef std::vector<shared_ptr<promise<SharedCloudType> > > Promises;

private:
    Futures futures;
    std::thread thread;

public:
    PointCloudProvider(int width, int height, int count=3, float vmax=0.5, float offset=0.0);
    ~PointCloudProvider();
    const CloudType& get();
};

namespace _CloudIntern {
    template<bool C> struct IndexType;

    template<> struct IndexType<true> {
        typedef uint16_t type;
    };

    template<> struct IndexType<false> {
        typedef uint32_t type;
    };
}

/**
 * The Pointcloud contains an especially assigned array of points
 * These points are randomly generated, sorted and at least they are "linked"
 * to their nearest neighbours
 * The creation of a PointCloud is connected with high computationally costs, so
 * it's recommended to create a bunch of clouds and afterwards using some pregenerated
 * to avoid expensive neighbour searches
 * When accessing to points you cannot enforce to following points with the same incresing x coordinates
 * to have the same y coordinate. It's only guaranteed, that the combination of both coordinates is
 * bigger equal to any proceeder.
 */
template<int N, int K = 24>
class PointCloud {
public:
    // Abhängig von der Anzahl der Punkte unterschiedlichen Typ für Index
    // verwenden. Porno!
    typedef typename _CloudIntern::IndexType<N <= 0xffff>::type Index;
    typedef Point<K, Index> PointType;

    // Für foreach
    typedef typename std::array<PointType, N>::iterator iterator;
    typedef typename std::array<PointType, N>::const_iterator const_iterator;

    enum {
        n = N,
        k = K
    };

private:
    int width, height;
    std::array<PointType, N> cloud;

    /**
     * This is an internal method to generate a random distribution of points, that follow some constrains like
     * a higher density in the upper part of the image.
     * \param matrix: Output parameter to store the points
     * \param verteilungsmaximum: Influences the point of the highest density
     */
    inline
    void generate_random_points(Eigen::MatrixXf& matrix, const float vmax, const float offset) const;

public:
    /**
     * The Constructor
     * \param width: Image width
     * \param height: Image height
     * \param vmax: the points, where the created distribution shall have the most density, values in range (0,1) are valid
     * \param offset: an offset to the point of the max density on the y-axis, needed for the new distribution functions since 9.2014
     */
    inline PointCloud(const int width,
        const int height, float vmax=0.5, float offset=0.0);

    const PointType& get_point(int idx) const {
        return cloud[idx];
    }

    int size() const {
        return N;
    }

    int get_width() const {
        return width;
    }

    int get_height() const {
        return height;
    }

    iterator begin() {
        return cloud.begin();
    }

    const_iterator begin() const {
        return cloud.begin();
    }

    iterator end() {
        return cloud.end();
    }

    const_iterator end() const {
        return cloud.end();
    }
};

} } //namespace

#endif

