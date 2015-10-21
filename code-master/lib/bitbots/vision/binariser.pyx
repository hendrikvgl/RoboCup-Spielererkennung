from libcpp.list cimport list
cimport eigen


cdef import from "binariser.hpp":
    cdef binarize_RGB(eigen.MatrixVec3b input, eigen.MatrixXb output)
