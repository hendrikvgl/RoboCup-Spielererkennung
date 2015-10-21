.. _pointcloud:

Pointcloud
==========

The pointcloud is a randomly generated set of points. The points aren't normally distributed in the picture.
The points are assorted inside the cloud. Each point saves it index inside the cloud and a specific number of nearest neighbours by cloud index and distance.

Methoden:
---------

.. cpp:class:: Point<N, Index>

	.. cpp:function:: int get_nn_count() const
		
		Gibt die Anzahl der nearest neighbours zurück.
		
	.. cpp:function:: Index get_nn_index(int nr) const
	
		Gibt den Index zurück.
		
	.. cpp:function:: float get_nn_distance(int nr) const
		
		Gibt die Distanz zu einem Nachbarn wieder.
		
	.. cpp:function:: void add_nn_index(Index idx, float distance)
	
		Fügt einen Nachbarn mit einem Index und einer Entfernung hinzu.
		
	.. cpp:function:: const Vector2x get_position() const
	
		Gibt die Position zurück.
		
.. cpp:class:: PointCloud

	.. cpp:function:: const PointType& get_Point(int idx)

		returns a specific point, if the index is valid

	.. cpp:function:: int size() const 

	        returns the number of Points inside the cloud
    
    	.. cpp:function:: int get_width() const

		returns width of the analysed picture
    
	.. cpp:function:: int get_height() const

		returns the height of the analysed picture
    
	.. cpp:function:: iterator begin()

		TODO
    
	.. cpp:function:: const_iterator begin() const

		TODO
    
	.. cpp:function:: iterator end()

		TODO
    
	.. cpp:function:: const_iterator end() const

		TODO
