from eigen cimport *
from cython.operator cimport dereference as deref
from cython.operator cimport address as ref
from libcpp.vector cimport vector
from bitbots.robot.pose cimport Pose
from bitbots.robot.pypose cimport PyPose
from bitbots.robot.kinematics cimport _Robot
from debugserver cimport _Shape
from bitbots.vision.robotvision cimport _ColorSample, _LineSample
from bitbots.robot.kinematics cimport _Robot
from bitbots.locator.transformer cimport _Transformer, Transformer


from libcpp cimport bool


cdef extern from "locator.hpp":
    cdef cppclass _Locator "Location::Locator":
        _Locator(_Transformer& transformer)
        void update(vector[_LineSample]& points, Vector3f movement) nogil except +
        vector[_Shape] get_debug_shapes()
        Vector3f get_position()
        void set_transformer(_Transformer& transformer)
        _Transformer& get_transformer()
        void set_position_information(Matrix2f)
        void say_robot_in_own_half()
        void say_robot_out_of_field()
        void say_robot_out_of_field_long_side()
        void say_robot_out_of_field_short_side()
        void say_robot_is_goalie()
        void reset_information()
        _Line_Samples make_field_model()

cdef extern from "noop_position_filter.hpp":
    cdef cppclass _Filter "Location::Noob_Position_Filter":
        _Filter()
        void set_position_information(Matrix2f& position)
        void reset_information()
        void set_additional_position_info(vector[Matrix2f]& position_limitations)
        void set_ball_pos(Vector2f position)
        void set_global_ball_pos(Vector2f position)
        void update(vector[Matrix3_2f]& position_suggestions, Vector3f movement)
        Vector3f get_position()


cdef extern from "line_sampler.hpp":
    cdef cppclass _Line "Line":
        _Line()
        _Line(Vector2f b, Vector2f e, Vector2f d)
        Vector2f begin
        Vector2f end
        Vector2f direction

    cdef cppclass _Circle "Circle":
        _Circle()
        _Circle(Vector2f m, float r)
        Vector2f midpoint
        float radius

    cdef cppclass _Line_Samples "Line_Samples":
        _Line_Samples(vector[_Line]& lines, vector[_Circle]& circles,
            vector[Vector2f]& points)
        vector[_Line]& lines
        vector[_Circle]& circles
        vector[Vector2f]& points

    cdef cppclass _Sampler "Location::Line_Sampler":
        _Sampler(_Transformer& transformer)
        _Transformer& get_transformer()
        void update(vector[_LineSample]& line_points)
        vector[_Shape]& get_debug_shapes()
        _Line_Samples& get_line_samples()


cdef extern from "line_matcher.hpp":
    cdef cppclass _Matcher "Location::Line_Matcher":
        _Matcher(_Line_Samples fieldmodel)
        void update(_Line_Samples& line_samples)
        vector[_Shape]& get_debug_shapes()
        vector[Matrix3_2f] get_suggested_positions()


cdef inline list wrap_line_samples(_Line_Samples line_samples, bool new_allocated):
    cdef vector[_Line] s_lines = line_samples.lines
    cdef int idx = 0
    cdef list lines = []
    cdef _Line line
    for idx in range(s_lines.size()):
        line = s_lines.at(idx)
        lines.append(((line.begin.x(), line.begin.y()),(line.end.x(), line.end.y()),
            (line.direction.x(), line.direction.y())))

    idx = 0
    cdef vector[_Circle] s_circles = line_samples.circles
    cdef list circles = []
    cdef _Circle circle
    for idx in range(s_circles.size()):
        circle = s_circles.at(idx)
        circles.append(((circle.midpoint.x(), circle.midpoint.y()), circle.radius))

    idx = 0
    cdef vector[Vector2f] s_points = line_samples.points
    cdef list points = []
    cdef Vector2f point
    for idx in range(s_points.size()):
        point = s_points.at(idx)
        points.append((point.x(), point.y()))

    #cdef vector[_Line]* l =  ref(s_lines)
    #cdef vector[_Circle]* c =  ref(s_circles)
    #cdef vector[Vector2f]* p =  ref(s_points)
    #if new_allocated:
    #    del l
    #    del c
    #    del p
    cdef list mixed = []
    mixed.append(lines)
    mixed.append(circles)
    mixed.append(points)
    return mixed

cdef inline _Line_Samples* extract_line_samples(list lines, list circles ,list points):
    cdef vector[_Line]* v_lines = new vector[_Line]()
    cdef int idx = 0
    cdef float xx = 0
    cdef float xy = 0
    cdef float xz = 0
    cdef float yx = 0
    cdef float yy = 0
    cdef float yz = 0
    cdef _Line line
    for idx in range(len(lines)):
        (xx,yx),(xy,yy),(xz,yz) = lines[idx]
        v_lines.push_back(_Line(Vector2f(xx,yx),Vector2f(xy,yy),Vector2f(xz,yz)))
    idx = 0
    cdef _Circle circle
    cdef vector[_Circle]* v_circles = new vector[_Circle]()
    for idx in range(len(circles)):
        (xx,yx),xz = circles[idx]
        v_circles.push_back(_Circle(Vector2f(xx,yx), xz))
    idx = 0
    cdef vector[Vector2f]* v_points = new vector[Vector2f]()
    for idx in range(len(points)):
        xx, yx = points[idx]
        v_points.push_back(Vector2f(xx,yx))
    cdef _Line_Samples* ls =  new _Line_Samples(deref(v_lines), deref(v_circles), deref(v_points))
    return ls


