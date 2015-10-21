from libcpp.list cimport list
cimport eigen


cdef import from "simple_vectorizer.hpp" namespace "Vision::ObstacleDetection":
    ctypedef struct pylon:
        pass
    cdef list findPylons(list &liste)
    cdef vectorize(eigen.MatrixHolder[eigen.MatrixXb] I, list &finished)

cdef initvectorizer():
    pass
