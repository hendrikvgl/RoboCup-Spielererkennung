from libcpp cimport bool
from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.string cimport string

from libc.stdint cimport *

cimport eigen

cdef extern from "memory" namespace "std":
    cdef cppclass SharedPointer "std::shared_ptr" [T]:
        T* get()

cdef extern from "debug_paint.hpp":
    cdef cppclass _Shape "Debug::Paint::Shape":
        string get_type()
        string get_text()
        map[string, float] get_values()

cdef extern from "debug_server.hpp" namespace "Debug::server":
    cdef cppclass Context:
        Context(char* data)

        string get_name()
        uint8_t get_type()

        # Simple Datentypen
        void get_object(int8_t&)
        void get_object(int16_t&)
        void get_object(int32_t&)
        void get_object(int64_t&)
        void get_object(float&)
        void get_object(double&)

        # std::string
        void get_object(string&)

        # OpenCV Vektoren (TODO mehr noch)
        void get_object(eigen.Vector2f&)
        void get_object(eigen.Vector3f&)
        void get_object(eigen.Vector4f&)

        # Eigen Matrix
        void get_object(eigen.RMatrixXbHolder&)
        void get_object(eigen.RMatrixVec3bHolder&)

        # Debug::Paint::Shape
        void get_object(_Shape&)
        void get_object(vector[_Shape]&)

    SharedPointer[Context] make_context(char*, int n) except +

cdef extern from "debug_type_info.hpp" namespace "Debug":
    cdef enum DebugType:
        BOOL, UCHAR, USHORT, UINT, ULONG, CHAR, SHORT, INT, LONG, FLOAT, DOUBLE, STRING, \
        SHAPE, SHAPE_VECTOR ,BWMATRIX, RGBMATRIX, LOG, WARNING

ctypedef DebugType _DebugType
