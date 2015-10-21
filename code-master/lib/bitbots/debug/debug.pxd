from libcpp cimport bool
from libcpp.string cimport string

cdef extern from "debug.hpp":
    cdef cppclass CScope "Debug::Scope":
        CScope(char*, bool)
        void operator<<(char*)

        void log(char*, float)
        void log(char*, int)
        void log(char*, string&)
        void warning(char*, char*)

        bool to_bool "operator bool" ()

cdef class Scope:
    cdef bytes name
    cdef bool console_out
    cdef CScope *scope

    cpdef Scope sub(self, name, console_out = ?)

