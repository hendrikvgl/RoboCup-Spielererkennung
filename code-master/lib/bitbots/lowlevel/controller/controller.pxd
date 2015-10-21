from libc.stdint cimport uint8_t
#from bitbots.lowlevel.controller.converter cimport Converter
from bitbots.lowlevel.controller.register_tables cimport Register

from bitbots.lowlevel.serial cimport AbsSerial
from bitbots.lowlevel.controller.register_tables cimport MX28RegisterTable, CM730RegisterTable

ctypedef uint8_t ubyte


cdef class BytePacket:
    cdef int idx
    cdef ubyte buffer[512]

    cdef void add_byte(self, ubyte b)
    cdef ubyte* advance(self, int n)
    cdef Processor get_processor(self)

cdef class Processor:
    cdef int count
    cdef int length
    cdef int get_answer_length(self)
    cdef int get_answer_count(self)
    cdef process(self, list packets)
    cdef int noanswer(self)

cdef class BulkReadPacket(BytePacket):
    cdef BulkReadProcessor processor
    cdef list registers

cdef class BulkReadProcessor(Processor):
    cdef list registers

cdef class SyncWritePacket(BytePacket):
    cdef tuple registers
    cdef add_header(self)
    cpdef add(self, int cid, tuple values)

cdef class Controller:
    cdef public AbsSerial serial

    cpdef process(self, BytePacket packet)
    cdef send_packet(self, BytePacket packet)
    cdef list read_packets(self, int count, int bytecount)
    cpdef read_register(self, int cid, Register register)
    cpdef write_register(self, int cid, Register register, object value)
    cpdef ping(self, int cid)

cdef MX28RegisterTable MX28
cdef CM730RegisterTable CM730

cdef int ID_BROADCAST
cdef int ID_CM730

