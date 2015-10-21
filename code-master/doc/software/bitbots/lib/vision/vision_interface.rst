.. _ip-vision:

Bildverarbeitung
================

The vision processes the images. 

Methoden
--------

.. cpp:class:: RawYUYVAdapter

	TODO

	.. cpp:function:: int get_width() const

	.. cpp:function:: int get_height() const

	TODO rest

.. cpp:class :: RobotVision

	.. cpp:function:: void set_carpet_threshold(int y, int u, int v)

		sets the carpet threshold

	.. cpp:function:: void set_color_config(const Eigen::DenseBase<Derived>& color_config)

	.. cpp:function:: void add_to_color_config(int x, int y, int flag)

	.. cpp:function:: void reset_color_config()

	.. cpp:function:: const BallInfo& get_ball_info() const

	.. cpp:function:: const GoalInfo& get_goal_info() const

	.. cpp:function:: const std::list<Pylon>& get_pylons() const

	.. cpp:function:: const std::list<ShapeVector>& get_shape_vectors() const

	.. cpp:function:: void process(const ImageType& input)

	.. cpp:function:: const std::vector<pa::Shape>& get_debug_shapes() const

	.. cpp:function:: const std::vector<Eigen::Vector2f>& get_line_points() const

