from cython.operator cimport postincrement as inc
from cython.operator cimport dereference as deref

from libcpp cimport bool
from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.string cimport string

cimport numpy as np
np.import_array()

from eigen cimport *
from debugserver cimport _Shape

#ColorSample und LineSample als Teil der LinePoints der Vision hier definiert
cdef extern from "../vision/sample.hpp":
    cdef cppclass _ColorSample "Vision::Sample::ColorSample":
        _ColorSample(Vector2f& pos, int index)
        _ColorSample()
        int get_index()
        float x()
        float y()

cdef extern from "../vision/sample.hpp":
    cdef cppclass _LineSample "Vision::Sample::LineSample":
        _LineSample(_ColorSample& sample, int parent)
        _LineSample()
        int get_index()
        int get_parent()
        float x()
        float y()

cdef inline list wrap_debug_shapes(vector[_Shape]& debug_shapes):
    cdef int idx
    cdef _Shape shape
    cdef map[string, float].iterator it

    cdef dict values
    cdef list shapes = []
    #@Robert 18.05.2014 The Shape doesn't hold the map anymore, so we need it here in place
    cdef map[string, float] value_map
    for idx in range(debug_shapes.size()):
        shape = debug_shapes.at(idx)
        values = {}
        value_map = shape.get_values()
        it = value_map.begin()
        while it != value_map.end():
            values[<char*>deref(it).first.c_str()] = deref(it).second
            inc(it)

        values["text"] = shape.get_text().c_str()
        shapes.append((shape.get_type().c_str(), values))

    return shapes

cdef inline MapRMatrixXb* vision_numpy_array_to_eigen_mat(np.ndarray ndarr):
    if ndarr.ndim != 2:
        raise ValueError("Invalid shape")

    cdef int width, height
    height, width = ndarr.shape[0], ndarr.shape[1]

    # Matrix erzeugen und Vision aufrufen!
    cdef char *data = np.PyArray_BYTES(ndarr)
    cdef MapRMatrixXb* image = new MapRMatrixXb(data, height, width)
    return image

cdef class LinePoints:
    cdef vector[_LineSample]* points
    cdef bool points_available
    cdef bool is_reference

    #Nur aufrufen, wenn man die LinePoints manuell gesetzt hat
    cdef void set_points(self, vector[_LineSample]* points, bool reference)
    cdef vector[_LineSample]* get_points(self) nogil
    cdef bool points_set(self)
    cpdef tuple get_point(self, idx)
    cpdef np.ndarray get_line_points(self)
