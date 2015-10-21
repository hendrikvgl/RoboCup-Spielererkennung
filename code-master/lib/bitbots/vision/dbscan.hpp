#ifndef _DBSCAN_HPP
#define _DBSCAN_HPP

#include <vector>
#include <Eigen/Core>

#include <utility>
#include <boost/scoped_ptr.hpp>
#include <boost/make_shared.hpp>
#include <boost/foreach.hpp>
#include <Eigen/StdVector>

#include "sample.hpp"
#include "common_type_definitions.hpp"

#define reverse_foreach BOOST_REVERSE_FOREACH
#define foreach BOOST_FOREACH

namespace Vision{
namespace Scanning{

/*
 * This namespace is used to define a type dynamicly according to template parameters
 * This namespace takes 2 template arguments and defines a struct. Now the struct templates are
 * specialized:
 * The Uses of this class then will be template specialized to define the correct types.
 */
namespace _Intern{
  template<class T, bool b> struct SampleType;

  template<> struct SampleType<LineClusteringSampleType, true>{
      typedef Sample::VisionLineSample type;
  };

  template<> struct SampleType<Sample::ColorColorSample, false>{
      typedef std::reference_wrapper<const Sample::ColorColorSample> type;
  };

  template<> struct SampleType<Sample::VisionSample, false>{
      typedef std::reference_wrapper<const Sample::VisionSample> type;
  };
}

/**
 * This class provides two ways of clustering points in connected components.
 * The first one, the more basic way is collecting points that are close to each other in a set.
 *
 * The second way just collects the outer points of these connected components and builds up an index based structure to
 * mark point as a parent of other points. Parent means a point in the set that is eigthrt a neighbour, or is the point
 * that was added last to the set and is connected through this neighbour relationship to this point.
 *
 * @Robert 07.04.2015
 * The new feature which limits the number of clustered pixels may harm the results of the clustering.
 * The main idea behind this is runtime optimization, because clustering too many points takes much time.
 * This can cause a split up of huge clusters, because this implicitly defines also a maximum cluster size.
 * Additionally the samples are iterated in reverse order to start from the bottom and not from the start.
 * This clusters those pixel, which lay potentially over the horizon last.
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
class SpatialClustering {
public:
    typedef std::reference_wrapper<const SampleType> SampleRef;
    //Having the goal to unite the two Clustering classes: Defining the Cluster Type depending on the template arguments.
    typedef typename _Intern::SampleType<SampleType, lines>::type ClusterType;
    typedef std::vector<ClusterType> Cluster;
    typedef std::vector<SampleRef> Region;

    enum { NOISE = 0,NONE = -1 };

private:
    const Cloud& m_cloud;
    const std::vector<SampleType>& m_samples;

    std::vector<Cluster> m_clusters;
    std::vector<char> m_visited;
    std::vector<int> m_labels, m_cloud_to_sample;

    float m_radius, m_acception_factor;
    int m_point_index;
    size_t m_min_points, m_max_clustering_size, m_num_clustered;

    void scan();
    void prepare();
    void expand(const SampleType& base, Region& region);
    bool region_query(const SampleType& midpoint, Region& region);
    void increase_parent(int index, int parent);
    void finish_abort_by_pixelcount();

    inline
    void classify(const SampleType& sample, int label);

public:
    SpatialClustering(const Cloud& cloud, const std::vector<SampleType>& samples,
            int radius=16, int min_points=5, float acception_factor = 0.45)
        : m_cloud(cloud), m_samples(samples), m_radius(radius),
         m_acception_factor(acception_factor), m_min_points(min_points), m_max_clustering_size((size_t)-1) {
        prepare();
        scan();
    }
    SpatialClustering(const Cloud& cloud, size_t max_clustering_size,
            const std::vector<SampleType>& samples, int radius=16, int min_points=5)
        : m_cloud(cloud), m_samples(samples), m_radius(radius), m_acception_factor(0.45),
         m_min_points(min_points), m_max_clustering_size(max_clustering_size), m_num_clustered(0) {
        prepare();
        scan();
    }

    const std::vector<Cluster>& get_clusters() const {
        return m_clusters;
    }
};

/**
 * Classifies a given sample, meaning storing it in the belonging sample container
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
void SpatialClustering<Cloud, SampleType, use_distance, lines>::classify(const SampleType& sample, int label) {
    m_labels[sample.get_index()] = label;
    m_clusters[label].emplace_back(sample);
}

/**
 * This is a template specialized version of the main classifying.
 * To the main classifying the parent relationship is build up
 */
template<>
void SpatialClustering<Cloud, LineClusteringSampleType, line_clustering_uses_distances, true>::classify(const LineClusteringSampleType& sample, int label) {
    m_clusters[label].emplace_back(sample, m_labels[sample.get_index()]);
    ++m_point_index;
}

/**
 * Increases the index of a parent in the given parent structure
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
void SpatialClustering<Cloud, SampleType, use_distance, lines>::increase_parent(int index, int parent)
{
    if(m_labels[index] < parent)
    {
        m_labels[index] = parent;//Marking the Current Point as the parent of the next ones
    }

}

/**
 * Prepares the main scan routine.
 * The using container are resized and prepared
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
void SpatialClustering<Cloud, SampleType, use_distance, lines>::prepare() {
    m_visited.resize(Cloud::n, false);
    m_labels.resize(Cloud::n, NONE);
    m_point_index = 0;

    m_cloud_to_sample.resize(Cloud::n, -1);

    for(unsigned i = 0; i < m_samples.size(); i++)
        m_cloud_to_sample[m_samples[i].get_index()] = i;

    m_clusters.clear();
    m_clusters.push_back(Cluster());
}

/**
 * \brief The main part, the scanning.
 *
 * This method visits every point of the given cluster and tries to create the
 * maximum connected component. Samples that are already part of an component won't be processed twice
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
void SpatialClustering<Cloud, SampleType, use_distance, lines>::scan() {
    reverse_foreach(const SampleType& sample, m_samples) {
        if(m_visited[sample.get_index()])
            continue;
        if(m_max_clustering_size < m_num_clustered) {
            finish_abort_by_pixelcount();
            break;
        }

        // als besucht markieren
        m_visited[sample.get_index()] = true;

        // Region mit Nachbarn suchen
        Region region;
        region_query(sample, region);
        if(region.size() < m_min_points) {
            if(not lines){
                classify(sample, NOISE);
            }
        } else {
            expand(sample, region);
        }
    }
}

/**
 * Expands a region of "connected" points
 * Adds nearest neighbours of the points inside the region
 * Not every point that could be inside will be added to the region
 * It's tried to add boundary points only.
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
void SpatialClustering<Cloud, SampleType, use_distance, lines>::expand(const SampleType& base, Region& region) {
    int label = m_clusters.size();

    m_clusters.push_back(Cluster());
    classify(base, label);

    for(size_t i = 0; i < region.size(); i++) {
        const SampleType& sample = region[i];
        if(!m_visited[sample.get_index()]) {
            m_visited[sample.get_index()] = true;
            // Abort clustering, when the cluster is too big
            if(region.size() > m_max_clustering_size / 3)
                break;
            Region next_region;
            region_query(sample, next_region);
            // Abort clustering, when the number of samples is too high
            if(m_num_clustered < m_max_clustering_size && next_region.size() >= m_min_points) {
                // region.insert(region.begin(), next_region.begin(), next_region.end());
                for(size_t j = 0; j < next_region.size(); j++) {
                    if(!m_visited[next_region[j].get().get_index()]) {
                        m_num_clustered++;
                        region.push_back(next_region[j]);
                    }
                }
            }
            else
                classify(sample, NOISE);
        }

        if(m_labels[sample.get_index()] == NONE)
            classify(sample, label);
    }

    if(m_clusters[label].size() <= 2*m_min_points) {
        foreach(const SampleType& sample, m_clusters[label])
            classify(sample, NOISE);

        m_clusters.pop_back();
        label--;
    }
}

/**
 * Expands a region of "connected" points
 * Adds nearest neighbours of the points inside the region
 * Not every point that could be inside will be added to the region
 * It's tried to add boundary points only.
 */
template<>
void SpatialClustering<Cloud, LineClusteringSampleType, line_clustering_uses_distances, true>::expand(const LineClusteringSampleType& base, Region& region) {
    int label = m_clusters.size();

    m_clusters.push_back(Cluster());

    m_labels[base.get_index()] = m_point_index;//Classify Cluster begin as its parent
    for(unsigned i = 0; i< region.size(); ++i)
    {
        m_labels[region[i].get().get_index()] = m_point_index;//Classify the parent of the first points of the cluster
    }//This needs to be before classifying the base, because classify increments _point_index
    classify(base, label);

    for(size_t i = 0; i < region.size(); i++) {
        const LineClusteringSampleType& sample = region[i];
        if(!m_visited[sample.get_index()]) {
            m_visited[sample.get_index()] = true;

            Region next_region;
            int parent = m_labels[sample.get_index()];
            if(!region_query(sample, next_region))//result determins, wheather sample is an inner point or not//we don't need inner points
            {
                parent = m_point_index;//Point index will be the current index in a list of all points// Deleting points will destroy this structure :(
                classify(sample, label);
            }
            for(size_t j = 0; j < next_region.size(); j++) { //adding valid non-visited samples to region
                if(!m_visited[next_region[j].get().get_index()]) {
                    region.push_back(next_region[j]);
                    LineClusteringSampleType s = next_region[j];
                    increase_parent(s.get_index(), parent);
                }
            }
        }
    }
}

/**
 * Makes a region query. Finds those points, which are close to the given Point
 * Return true, if there are "to many" points around that one in the given Collection
 */
template<class Cloud, class SampleType, bool use_distance, bool lines>
bool SpatialClustering<Cloud, SampleType, use_distance, lines>::region_query(const SampleType& mid, Region& region) {
    int invalid_neighbours = 0;
    const typename Cloud::PointType& point = m_cloud.get_point(mid.get_index());
    for(int i = 0; i < point.get_nn_count(); i++) {
        int idx = m_cloud_to_sample[point.get_nn_index(i)];
        if(idx > -1) {
            //Berücksichtige die "Distanz" der Punkte, wenn der Templateparameter an fordert
            /*the mid .template call is the result of an clang/gcc "referece to non static member must be called" error.
             * gcc interpreted the template specefier "<" as operator :( */
            if(not use_distance || mid.template is_close_to<Sample::SamplingDistanceType::FULL_DIST>(m_samples[idx])){
                region.emplace_back(m_samples[idx]);
            }
        }
        else
        {
            ++invalid_neighbours;
        }
    }
    return lines && (point.get_nn_count() * m_acception_factor > invalid_neighbours);//true will ignore Point
}


template<class Cloud, class SampleType, bool use_distance, bool lines>
void SpatialClustering<Cloud, SampleType, use_distance, lines>::finish_abort_by_pixelcount() {
    m_clusters.push_back(Cluster());
    foreach(const SampleType& sample, m_samples) {
        if(m_visited[sample.get_index()])
            continue;
        m_clusters.back().emplace_back(sample);
    }
}
template<>
void SpatialClustering<Cloud, LineClusteringSampleType, line_clustering_uses_distances, true>::finish_abort_by_pixelcount() {
    m_clusters.push_back(Cluster());
    foreach(const LineClusteringSampleType& sample, m_samples) {
        if(m_visited[sample.get_index()])
            continue;
        m_clusters.back().emplace_back(sample, m_labels[sample.get_index()]);
    }
}

//Clean up
#undef foreach
} }//namespace Vision
#endif

