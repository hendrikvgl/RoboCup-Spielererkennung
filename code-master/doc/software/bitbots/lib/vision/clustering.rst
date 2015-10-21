.. _ip-clustering:

Clustering
==========

The clusterer is working on pointcloud based structures. The clustering is able to find points, which lay nearby each ohter inside the cloud. These points are collected in a cluster.

Methods
-------

.. cpp:class:: SpatialClustering

    .. cpp:function:: void SpatialClustering(const cloud& cloud, const std::vector<ColorSample>& samples, float radius, int min_points)

		First of all the constructor initialises the local fields with the given parameters.
		After that the points are prepared to scan and scanned.

	.. cpp:function:: prepare()

		Prepares some extra field for scanning. Such as the vectors cloud_to_sample, labels, visited.
		The indeces of these vectors are the same indices, as in the pointcloud where the samples come from. So if the point with cloud index 1 is one of the samples, index 1 in all of these vectors is representing it.
		cloud_to_sample represents the index of any point in the samples vector or -1, if it's none of the samples.
		visited represents all of the processed and visited points.
		label represents the cluster containing the requested point.

	.. cpp:function:: scan()

		Goes through every point of the samples and first makes a region_query. If there are more than the given minimum of points inside the cluster the region is expanded. If not, the point is classified as noise.

	.. cpp:function:: expand(const ColorSample& base, Region& region)

		Expands a given region with points laying close to other points inside the given region. This process contians the following steps for every the points inside the region.

		* Marking a point as visited
		* Querying the nearest cloud neighbouors by reqion_query
		* Adding every point of the new region to the expanded one, if the queried point has the minimun of nearest neighbours in the samples vector
		* Classifying the points as points of the expanded region using classify

		If the cluster is to small, the points inside the cluster are classified as noise.

	.. cpp:function:: region_query(const ColorSample& midpoint, Region& region)

		Goes through the nearest neighbours in the cloud of the midpoint. Every neighbour which is part of the samples is added to the region.

	.. cpp:function:: classify(const ColorSample& sample, int label)

		Classifies a point as part of a cluster and adds the point to the cluster.

	.. cpp:function:: get_clusters()

		Returns the clusters, which are the result of scanning and clustering.
