from cython.operator cimport dereference as deref
from cython.operator cimport address as ref
from eigen cimport *
from libcpp.vector cimport vector
from bitbots.robot.pose cimport Pose
from bitbots.robot.pypose cimport PyPose
from bitbots.vision.robotvision cimport wrap_debug_shapes, _ColorSample, _LineSample, LinePoints
from bitbots.robot.kinematics cimport Robot, _Robot
from debugserver cimport _Shape
from bitbots.locator.transformer cimport _Transformer, Transformer

import numpy as np
cimport numpy as np
np.import_array()

from libcpp cimport bool

cdef class Locator:
    cdef _Locator *locator

    def __cinit__(self, Transformer transformer):
        self.locator = new _Locator(deref(transformer.transformer))

    def __dealloc__(self):
        del self.locator

    def update(self, LinePoints points not None, float m_x, float m_y, float m_z):
        print points.points_set()
        if points.points_set() is True:
            with nogil:
                self.locator.update(deref(points.points), Vector3f(m_x, m_y, m_z))
            print "Done"

    def get_debug_shapes(self):
        return wrap_debug_shapes(self.locator.get_debug_shapes())

    def get_position(self):
        result = self.locator.get_position()
        return (result.x(), result.y(), result.z())

    def set_transformer(self, Transformer transformer):
        self.locator.set_transformer(deref(transformer.transformer))

    def get_transformer(self):
        t = Transformer()
        #deleting the "old" transformer to set a new one
        del t.transformer
        t.transformer = ref(self.locator.get_transformer())
        return t

    def reset_position_info(self):
        self.locator.reset_information()

    def say_robot_in_own_half(self):
        self.locator.reset_information()
        self.locator.say_robot_in_own_half()

    def say_robot_out_of_field_long_side(self):
        self.locator.reset_information()
        self.locator.say_robot_out_of_field_long_side()

    def say_robot_out_of_field_short_side(self):
        self.locator.reset_information()
        self.locator.say_robot_out_of_field_short_side()

    def say_robot_out_of_field(self):
        self.locator.reset_information()
        self.locator.say_robot_out_of_field()

    def say_robot_is_goalie(self):
        self.locator.reset_information()
        self.locator.say_robot_is_goalie()

    def get_field_model(self):
        return wrap_line_samples(self.locator.make_field_model(), True)

cdef class Sampler:
    cdef _Sampler* sampler

    def __cinit__(self, Transformer transformer):
        self.sampler = new _Sampler(deref(transformer.transformer))

    def __dealloc__(self):
        del self.sampler

    def update(self, np.ndarray arr not None):
        if arr.ndim != 2 and len(arr) != 0:
                raise ValueError("Invalid LineSamples")

        cdef vector[_LineSample] samples = vector[_LineSample]()
        for idx in range (len(arr)):
            (x,y,index,parent) = arr[idx]
            samples.push_back(_LineSample(_ColorSample(Vector2f(<double>x, <double>y), \
                    int(index)), int(parent)))

        self.sampler.update(samples)

    def get_line_samples(self):
        return wrap_line_samples(self.sampler.get_line_samples(), False)

    def get_debug_shapes(self):
        return wrap_debug_shapes(self.sampler.get_debug_shapes())


cdef class Matcher:
    cdef _Matcher* matcher

    def __cinit__(self):
        cdef Robot robot = Robot()
        cdef _Transformer* t = new _Transformer(deref(robot.robot))
        cdef _Locator* locator = new _Locator(deref(t))
        self.matcher = new _Matcher(locator.make_field_model())
        del locator
        del t

    def __dealloc__(self):
        del self.matcher

    def update(self, list lines, list circles, list points):
        cdef _Line_Samples* ls = extract_line_samples(lines, circles, points)
        self.matcher.update(deref(ls))
        cdef vector[_Line]* v_lines = ref(ls.lines)
        del v_lines
        cdef vector[_Circle]* v_circles = ref(ls.circles)
        del v_circles
        cdef vector[Vector2f]* v_points = ref(ls.points)
        del v_points
        del ls

    def get_debug_shapes(self):
        return wrap_debug_shapes(self.matcher.get_debug_shapes())

    def get_suggested_positions(self):
        cdef vector[Matrix3_2f] suggestions = self.matcher.get_suggested_positions()
        cdef list positions = []
        cdef Matrix3_2f pos
        cdef float x1, x2, x3, y1, y2, y3
        cdef int idx
        for idx in range(suggestions.size()):
            pos = suggestions[idx]
            x1 = pos.at(0,0)
            x2 = pos.at(1,0)
            x3 = pos.at(2,0)
            y1 = pos.at(0,1)
            y2 = pos.at(1,1)
            y3 = pos.at(2,1)
            positions.append(((x1, y1),(x2, y2),(x3, y3)))
        return positions

cdef class Filter:
    cdef _Filter* filter

    def __cinit__(self):
        filter = new _Filter()

    def set_position_information(self, x1, y1, x2, y2):
        cdef Matrix2f info
        #TODO Matrix ist nur default
        self.filter.set_position_information(info)

    def reset_information(self):
        self.filter.reset_information()

    def set_additional_position_info(self, infos):
        pass
        #TODO

    def set_ball_pos(self, x, y):
        self.filter.set_ball_pos(Vector2f(<double>x, <double>y))

    def update(self, positions, movement):
        pass

    def get_position(self):
        cdef Vector3f v
        v = self.filter.get_position()
        return (v.x(),v.y(),v.z())
"""
        void set_additional_position_info(vector[Matrix2f]& position_limitations)
        void set_ball_pos(Vector2f position)
        void set_global_ball_pos(Vector2f position)
        void update(vector[Matrix3_2f]& position_suggestions, Vector3f movement)
        Vector3f get_position()
"""
