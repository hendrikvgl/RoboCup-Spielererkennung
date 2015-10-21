#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy
cimport numpy

# Nötig, wenn man Numpy mit Cython nutzen will
numpy.import_array()

# OpenGL Funktionen importieren, die wir verwenden wollen
from c_opengl cimport *

ctypedef int bool

cdef class Vector3f:
    cdef public float x, y, z
    
    
cdef class Vector3i:
    cdef public int x, y, z
    
    
cdef class Node:
    cpdef render(self):
        pass
    
cdef class TransformNode(Node):
    cdef readonly Vector3f scale
    cdef readonly Vector3f position
    cdef readonly Vector3f rotation, rotation_offset
    cdef readonly Vector3i rotation_axis
    
    def __init__(self):
        self.scale = Vector3f()
        self.position = Vector3f()
        self.rotation = Vector3f()
        self.rotation_offset = Vector3f()
        self.rotation_axis = Vector3i()
        
        self.rotation_axis.x = 1
        self.rotation_axis.y = 1
        self.rotation_axis.z = 1
        
        self.scale.x = 1
        self.scale.y = 1
        self.scale.z = 1
    
    cpdef transform(self):
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation.x + self.rotation_offset.x, self.rotation_axis.x, 0, 0)
        glRotatef(self.rotation.y + self.rotation_offset.y, 0, self.rotation_axis.y, 0)
        glRotatef(self.rotation.z + self.rotation_offset.z, 0, 0 ,self.rotation_axis.z)
        glScalef(self.scale.x, self.scale.y, self.scale.z)
    
    cpdef set_scale(self, float x, float y, float z):
        self.scale.x = x
        self.scale.y = y
        self.scale.z = z
    
    cpdef set_position(self, float x, float y, float z):
        self.position.x = x
        self.position.y = y
        self.position.z = z
    
    cpdef set_rotation(self, float x, float y, float z):
        self.rotation.x = x
        self.rotation.y = y
        self.rotation.z = z
    
    cpdef set_rotation_offset(self, float x, float y, float z):
        self.rotation_offset.x = x
        self.rotation_offset.y = y
        self.rotation_offset.z = z
    
    cpdef set_rotation_axis(self, int x, int y, int z):
        self.rotation_axis.x = -1 if x < 0 else 1
        self.rotation_axis.y = -1 if y < 0 else 1
        self.rotation_axis.z = -1 if z < 0 else 1

    
cdef class Group(TransformNode):
    cdef list nodes
    
    def __init__(self, *nodes):
        super(Group, self).__init__()
        self.nodes = list(nodes)
    
    def add(self, Node node not None):
        self.nodes.append(node)
    
    def remove(self, Node node not None):
        if node in self.nodes:
            self.nodes.remove(node)
    
    def make(self, clazz not None):
        cdef Node node = clazz()
        self.add(node)
        return node
    
    cpdef render_nodes(self):
        cdef Node node
        for node in self.nodes:
            node.render()
    
    cpdef render(self):
        glPushMatrix()
        try:
            self.transform()
            self.render_nodes()
        finally:
            glPopMatrix()

cdef norm = numpy.linalg.norm
cdef numpy.ndarray normalize(numpy.ndarray v):
    return v / norm(v)

cdef class MatrixNode(Node):
    cdef numpy.ndarray matrix
    cdef Node node
    
    def __init__(self, Node node):
        self.node = node
        self.set_identity()
    
    def set_node(self, Node node):
        self.node = node
    
    def set_identity(self):
        self.set_matrix(numpy.eye(4, dtype=numpy.float32))
    
    def set_matrix(self, numpy.ndarray matrix not None):
        if matrix.dtype != numpy.float32:
            raise ValueError("Nur dtype=float32 zulässig")
        
        if matrix.ndim != 2 or matrix.shape[0] != 4 or matrix.shape[1] != 4:
            raise ValueError("Nur 4x4 Matrizen erlaubt")
        
        self.matrix = matrix.transpose().copy()
    
    def set_matrix_from_axis(self, numpy.ndarray direction, origin=None):
        cdef numpy.ndarray matrix = numpy.empty((4, 4), dtype=numpy.float32)
        
        # Einen Vektor finden, der nicht parallel zu direction liegt
        cdef tuple v1 = (0, 1, 0), v2 = (1, 0, 0)
        cdef tuple vec = v1 if abs(numpy.dot(direction, v1)) < abs(numpy.dot(direction, v2)) else v2
        
        matrix[:3,1] = direction[:3]
        matrix[:3,0] = normalize(numpy.cross(matrix[:3,1], vec))
        matrix[:3,2] = normalize(numpy.cross(matrix[:3,0], matrix[:3,1]))
        matrix[:3,3] = (0, 0, 0) if origin is None else origin
        matrix[3] = (0, 0, 0, 1)
        self.set_matrix(matrix)
    
    cpdef render(self):
        if self.node is None:
            return
        
        cdef float *data = <float*><char*>numpy.PyArray_BYTES(self.matrix)
        
        glPushMatrix()
        try:
            glMultMatrixf(data)
            self.node.render()
        finally:
            glPopMatrix()


cdef class Texture:
    cdef int tid
    
    def __cinit__(self, *args):
        glGenTextures(1, &self.tid)
    
    def __dealloc__(self):
        glDeleteTextures(1, &self.tid)
    
    def update(self, int width, int height, bytes pixels):
        self.bind()

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        if width*height*3 == len(pixels):
            glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
        elif width*height*4 == len(pixels):
            glTexImage2D(GL_TEXTURE_2D, 0, 4, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)
        else:
            raise ValueError("24- oder 32-bit RGB erwartet")
            
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
    cpdef bind(self):
        glBindTexture(GL_TEXTURE_2D, self.tid)

cdef class VertexBufferObject(Node):
    cdef public Texture texture
    cdef float[4] _color
    cdef int vbo_vertex, vbo_normal, vbo_texcoords
    cdef int ibo_indices
    
    cdef int count_indices
    cdef int count_vertices
    
    cdef bool has_indices
    cdef bool has_vertices, has_normals, has_texcoords
    cdef Vector3f scale
    
    def __cinit__(self, *args):
        glGenBuffers(1, &self.vbo_vertex)
        glGenBuffers(1, &self.vbo_normal)
        glGenBuffers(1, &self.vbo_texcoords)
        glGenBuffers(1, &self.ibo_indices)
    
    def __dealloc__(self):
        glDeleteBuffers(1, &self.vbo_vertex)
        glDeleteBuffers(1, &self.vbo_normal)
        glDeleteBuffers(1, &self.vbo_texcoords)
        glDeleteBuffers(1, &self.ibo_indices)
    
    def __init__(self):
        self.scale = Vector3f()
        self.scale.x = 1
        self.scale.y = 1
        self.scale.z = 1
        
        self._color[:] = [1, 1, 1, 1]
    
    cdef upload(self, int vbo, numpy.ndarray ndarr):
        if ndarr.dtype != numpy.float32:
            raise ValueError("Array hat den falschen Datentyp")
        
        cdef int size = numpy.PyArray_SIZE(ndarr) * 4
        cdef char *data = numpy.PyArray_BYTES(ndarr)
        
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, size, data, GL_STATIC_DRAW)
    
    def update_vertices(self, numpy.ndarray ndarr not None):
        if ndarr.ndim != 2 or ndarr.shape[1] != 3:
            raise ValueError("Array muss drei Spalten haben")
        
        self.upload(self.vbo_vertex, ndarr)
        self.has_vertices = True
        self.count_vertices = len(ndarr)
    
    def update_normals(self, numpy.ndarray ndarr not None):
        if ndarr.ndim != 2 or ndarr.shape[1] != 3:
            raise ValueError("Array hat die falsche Dimension")
        
        self.upload(self.vbo_normal, ndarr)
        self.has_normals = True
    
    def update_texcoords(self, numpy.ndarray ndarr not None):
        if ndarr.ndim != 2 or ndarr.shape[1] != 2:
            raise ValueError("Array hat die falsche Dimension")
        
        self.upload(self.vbo_texcoords, ndarr)
        self.has_texcoords = True
    
    def update_indices(self, numpy.ndarray ndarr not None):
        if ndarr.ndim != 2 or ndarr.shape[1] != 3:
            raise ValueError("Array hat die falsche Dimension")
        
        if ndarr.dtype != numpy.uint16:
            raise ValueError("IndexBuffer hat den falschen Datentyp")
        
        # Daten holen und zur Grafikkarte schicken
        cdef int size = numpy.PyArray_SIZE(ndarr) * 2
        cdef char *data = numpy.PyArray_BYTES(ndarr)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo_indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, size, data, GL_STATIC_DRAW)
        
        self.has_indices = True
        self.count_indices = 3 * len(ndarr)
    
    def set_color(self, float r, float g, float b, float a = 1):
        self._color[0] = r
        self._color[1] = g
        self._color[2] = b
        self._color[3] = a
    
    def set_alpha(self, float alpha):
        self._color[3] = alpha
    
    cpdef set_scale(self, float x, float y, float z):
        self.scale.x = x
        self.scale.y = y
        self.scale.z = z
    
    cpdef render(self):
        if not self.has_vertices:
            return
        
        cdef bool use_textures
        
        # Tranfsormation anwenden
        glPushMatrix()
        try:
            glScalef(self.scale.x, self.scale.y, self.scale.z)

            # Farbe setzen
            glColor4f(self._color[0], self._color[1], self._color[2], self._color[3])
            
            glEnableClientState(GL_VERTEX_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertex)
            glVertexPointer(3, GL_FLOAT, 0, <void*>0)
            
            if self.has_normals:
                glEnableClientState(GL_NORMAL_ARRAY)
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normal)
                glNormalPointer(GL_FLOAT, 0, <void*>0)
            
            use_textures = self.texture is not None and self.has_texcoords != False
            if use_textures:
                self.texture.bind()
                
                glEnable(GL_TEXTURE_2D)
                glEnableClientState(GL_TEXTURE_COORD_ARRAY)
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo_texcoords)
                glTexCoordPointer(2, GL_FLOAT, 0, <void*>0)
            
            if self.has_indices:
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo_indices)
                glDrawElements(GL_TRIANGLES, self.count_indices, GL_UNSIGNED_SHORT, <void*>0)
            else:
                glDrawArrays(GL_TRIANGLES, 0, self.count_vertices)
            
            if use_textures:
                glDisable(GL_TEXTURE_2D)
                glDisableClientState(GL_TEXTURE_COORD_ARRAY)
            
            if self.has_normals:
                glDisableClientState(GL_NORMAL_ARRAY)
            
            glDisableClientState(GL_VERTEX_ARRAY)
        
        finally:
            glPopMatrix()
        
