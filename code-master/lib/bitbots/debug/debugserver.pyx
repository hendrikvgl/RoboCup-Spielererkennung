# -*- encoding: utf8 -*-

from cython.operator cimport dereference as deref, postincrement as inc

import zlib
import struct
import gevent
import traceback

import numpy

from gevent.server import StreamServer
cimport eigen

cdef class Server:
    cdef object running
    cdef object server
    cdef list listeners

    def __init__(self, addr=("", 6482)):
        self.server = gevent.socket.socket(type=gevent.socket.SOCK_DGRAM)
        self.server.bind(addr)
        self.listeners = []
        self.running = True

    def add_listener(self, li):
        self.listeners.append(li)

    def remove_listener(self, li):
        if li in self.listeners:
            self.listeners.remove(li)

    def start(self):
        print "[DebugServer] Startup"
        gevent.spawn(self._loop)

    def stop(self):
        self.running = False
        self.server.close()

    def _loop(self):
        cdef bytes data
        try:
            while self.running:
                data = self.server.recv(1024 * 64)
                try:
                    data = zlib.decompress(data)
                    self.handle_message(data)

                except Exception, e:
                    print "[DebugServer]", e

        except IOError, e:
            print "[DebugServer]", e

        except KeyboardInterrupt:
            pass

    def handle_message(self, bytes data):
        cdef SharedPointer[Context] ctx = make_context(data, len(data))
        cdef bytes name = ctx.get().get_name().c_str()
        cdef uint8_t type = ctx.get().get_type()

        if type == LOG:
            self.handle_log_message(name, ctx)

        elif type == WARNING:
            self.handle_warning_message(name, ctx)

        # Primitive Datentypen
        elif (type == UCHAR or type == USHORT or type == UINT or type == ULONG \
                 or type == CHAR or type == SHORT or type == INT or type == LONG):
            self.handle_int_message(name, type, ctx)

        elif type == FLOAT or type == DOUBLE:
            self.handle_float_message(name, type == DOUBLE, ctx)

        elif type == BOOL:
            self.handle_bool_message(name, ctx)

        # Eigen Matrix mit einem Farbkanal
        elif type == BWMATRIX:
            self.handle_eigen_matrix_message(name, ctx, 1)

        # Eigen Matrix mit 3 Farbkanälen
        elif type == RGBMATRIX:
            self.handle_eigen_matrix_message(name, ctx, 3)

        # Strings
        elif type == STRING:
            self.handle_string_message(name, ctx)

        # Shapes
        elif type == SHAPE:
            self.handle_shape_message(name, ctx)

        elif type == SHAPE_VECTOR:
            self.handle_shape_vector_message(name, ctx)

        else:
            print "[DebugServer] Typ '%s' nicht unterstützt" % type

    cdef handle_log_message(self, name, SharedPointer[Context] ctx):
        cdef string message
        ctx.get().get_object(message)
        self.emit(b"log", name, message.c_str())

    cdef handle_warning_message(self, name, SharedPointer[Context] ctx):
        cdef string message
        ctx.get().get_object(message)
        self.emit(b"warning", name, message.c_str())

    cdef handle_string_message(self, name, SharedPointer[Context] ctx):
        cdef string message
        ctx.get().get_object(message)
        self.emit(b"string", name, message.c_str())

    cdef handle_bool_message(self, name, SharedPointer[Context] ctx):
        cdef bool value = False
        ctx.get().get_object(value)
        self.emit(b"bool", name, value)

    cdef handle_float_message(self, name, is_double, SharedPointer[Context] ctx):
        cdef float f_value = 0
        cdef double d_value = 0
        cdef object value
        if is_double:
            ctx.get().get_object(d_value)
            value = d_value
        else:
            ctx.get().get_object(f_value)
            value = f_value

        self.emit(b"number", name, value)

    cdef handle_int_message(self, name, type, SharedPointer[Context] ctx):
        cdef int8_t value_s8 = 0
        cdef int16_t value_s16 = 0
        cdef int32_t value_s32 = 0
        cdef int64_t value_s64 = 0

        cdef uint8_t value_u8 = 0
        cdef uint16_t value_u16 = 0
        cdef uint32_t value_u32 = 0
        cdef uint64_t value_u64 = 0

        if type == CHAR:
            ctx.get().get_object(value_s8)
            self.emit(b"number", name, value_s8)

        elif type == SHORT:
            ctx.get().get_object(value_s16)
            self.emit(b"number", name, value_s16)

        elif type == INT:
            ctx.get().get_object(value_s32)
            self.emit(b"number", name, value_s32)

        elif type == LONG:
            ctx.get().get_object(value_s64)
            self.emit(b"number", name, value_s64)

        elif type == UCHAR:
            ctx.get().get_object(value_u8)
            self.emit(b"number", name, value_u8)

        elif type == USHORT:
            ctx.get().get_object(value_u16)
            self.emit(b"number", name, value_u16)

        elif type == UINT:
            ctx.get().get_object(value_u32)
            self.emit(b"number", name, value_u32)

        elif type == ULONG:
            ctx.get().get_object(value_u64)
            self.emit(b"number", name, value_u64)

        else:
            print "[DebugServer] Ungültiger Integer Typ:", type

    cdef handle_shape_message(self, name, SharedPointer[Context] ctx):
        cdef _Shape shape
        ctx.get().get_object(shape)

        cdef dict values = {}
        #@Robert 18.05.2014 The Shape doesn't hold the map anymre, so we need it here in place
        cdef map[string, float] value_map = shape.get_values()
        cdef map[string, float].iterator it = value_map.begin()
        while it != value_map.end():
            values[< char * >deref(it).first.c_str()] = deref(it).second
            inc(it)

        values["text"] = shape.get_text().c_str()
        self.emit(b"shape", name, (shape.get_type().c_str(), values))

    cdef handle_shape_vector_message(self, name, SharedPointer[Context] ctx):
        cdef vector[_Shape] shapes
        cdef list result = []

        ctx.get().get_object(shapes)

        cdef int i
        cdef dict values
        #@Robert 18.05.2014 The Shape doesn't hold the map anymre, so we need it here in place
        cdef map[string, float] value_map
        cdef map[string, float].iterator it
        for i in range(shapes.size()):
            values = {}
            value_map = shapes.at(i).get_values()
            it = value_map.begin()
            while it != value_map.end():
                values[< char * >deref(it).first.c_str()] = deref(it).second
                inc(it)

            values["text"] = shapes.at(i).get_text().c_str()
            result.append((shapes.at(i).get_type().c_str(), values))

        self.emit(b"shapes", name, result)

    cdef handle_eigen_matrix_message(self, name, SharedPointer[Context] ctx, int channels):
        cdef eigen.RMatrixXbHolder matrix1
        cdef eigen.RMatrixVec3bHolder matrix3

        if channels == 1:
            ctx.get().get_object(matrix1)
        else:
            ctx.get().get_object(matrix3)

        # Daten
        cdef char * data
        cdef int bytecount
        if channels == 1:
            data = <char * >matrix1.ptr()
            bytecount = matrix1.size()
        else:
            data = <char * >matrix3.ptr()
            bytecount = matrix3.size()
        cdef object arr = numpy.fromstring(data[:bytecount], dtype=numpy.uint8)
        if channels == 1:
            arr = arr.reshape(matrix1.rows(), matrix1.cols())
        else:
            arr = arr.reshape(matrix3.rows(), matrix3.cols(), channels).copy()

        self.emit(b"matrix", name, arr)

    cdef emit(self, bytes type, bytes name, obj):
        for li in self.listeners[:]:
            try:
                li(type, name, obj)
            except:
                traceback.print_exc()


def serve():
    try:
        def listener(type, name, data):
            """ Einfach die Pakete auf der Konsole ausgeben """
            print name, "(%s)" % type, data

        s = Server()
        s.add_listener(listener)
        s.start()

    except KeyboardInterrupt:
        print "[DebugServer] Shutdown"
