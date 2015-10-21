from cython.operator cimport dereference as deref

from libcpp cimport bool
from libcpp.string cimport string

# NumPy importieren
cimport numpy as np
np.import_array()

from eigen cimport MapRMatrixXb, mutable_char_ptr

cdef extern from "noop_image_decoder.hpp":
    pass

cdef extern from "capture.hpp":
    cdef cppclass _VideoCapture "Vision::Video::VideoCapture":
        _VideoCapture()
        _VideoCapture(char*) except +

        void open(char*) except +
        void start() except +
        void set_pixel_format(char*, int width, int height) except +

        void set_noop_image_decoder "set_image_decoder<Vision::Video::Decoder::NoopImageDecoder>" ()
        void set_max_fps(unsigned int)

        int get_width()
        int get_height()

        MapRMatrixXb* grab() nogil except +

        Controller& get_controller(char*)

        Controller& get_brightness()
        Controller& get_contrast()
        Controller& get_saturation()
        Controller& get_hue()
        Controller& get_sharpness()
        Controller& get_gain()
        Controller& get_gain_auto()
        Controller& get_white_balance_temperature()
        Controller& get_white_balance_temperature_auto()
        Controller& get_exposure_auto()
        Controller& get_exposure_auto_priority()
        Controller& get_exposure_absolute()
        Controller& get_focus_absolute()
        Controller& get_focus_relative()
        Controller& get_focus_auto()

    cdef cppclass Controller:
        string get_name()
        float get_value()
        int get_value_raw()

        void set_bool(bool) except +
        void set_value(float) except +
        void set_value_raw(int) except +

cdef np.ndarray eigenmat_to_numpy(MapRMatrixXb* mat):
    if mat == NULL:
        exit(1)

    cdef np.npy_intp shape[3]
    shape[0] = mat.rows()
    shape[1] = mat.cols()
    shape[2] = 4

    cdef int cn = 2
    return np.PyArray_SimpleNewFromData(cn, shape, np.NPY_UBYTE, mutable_char_ptr(mat.data()))

cdef class VideoCapture:
    cdef _VideoCapture *capture
    cdef MapRMatrixXb *mat

    def __cinit__(self, bytes device, int width, int height):
        self.mat = NULL

        self.capture = new _VideoCapture(device)
        self.capture.set_pixel_format("YUYV", width, height)

    def __dealloc__(self):
        del self.capture
        del self.mat

    def start(self):
        self.capture.start()

    def set_noop_image_decoder(self):
        self.capture.set_noop_image_decoder()

    property max_fps:
        def __set__(self, int fps): self.capture.set_max_fps(fps)

    property width:
        def __get__(self): return self.capture.get_width()

    property height:
        def __get__(self): return self.capture.get_height()

    property size:
        def __get__(self): return (self.width, self.height)

    property brightness:
        def __get__(self): return self.capture.get_brightness().get_value()
        def __set__(self, float v): self.capture.get_brightness().set_value(v)

    property contrast:
        def __get__(self): return self.capture.get_contrast().get_value()
        def __set__(self, float v): self.capture.get_contrast().set_value(v)

    property saturation:
        def __get__(self): return self.capture.get_saturation().get_value_raw()
        def __set__(self, int v): self.capture.get_saturation().set_value_raw(v)

    property hue:
        def __get__(self): return self.capture.get_hue().get_value()
        def __set__(self, float v): self.capture.get_hue().set_value(v)

    property gain:
        def __get__(self): return self.capture.get_gain().get_value_raw()
        def __set__(self, int v): self.capture.get_gain().set_value_raw(v)

    property gain_auto:
        def __get__(self): return self.capture.get_gain_auto().get_value()
        def __set__(self, bool v): self.capture.get_gain_auto().set_bool(v)

    property white_balance:
        def __get__(self): return self.capture.get_white_balance_temperature().get_value()
        def __set__(self, float v): self.capture.get_white_balance_temperature().set_value(v)

    property white_balance_auto:
        def __get__(self): return self.capture.get_white_balance_temperature_auto().get_value()
        def __set__(self, bool v): self.capture.get_white_balance_temperature_auto().set_bool(v)

    property sharpness:
        def __get__(self): return self.capture.get_sharpness().get_value()
        def __set__(self, float v): self.capture.get_sharpness().set_value(v)

    property exposure_auto:
        def __get__(self): return self.capture.get_exposure_auto().get_value_raw()
        def __set__(self, int v): self.capture.get_exposure_auto().set_value_raw(v)

    property exposure_auto_priority:
        def __get__(self): return <bool>(self.capture.get_exposure_auto_priority().get_value())
        def __set__(self, bool v): self.capture.get_exposure_auto_priority().set_bool(v)

    property exposure_absolute:
        def __get__(self): return self.capture.get_exposure_absolute().get_value_raw()
        def __set__(self, int v): self.capture.get_exposure_absolute().set_value_raw(v)

    property focus_absolute:
        def __get__(self): return self.capture.get_focus_absolute().get_value_raw()
        def __set__(self, int v):
            if self.focus_auto:
                print "WARNING: focus_auto gesetzt, setze kein exposure_absolute!"
                return
            self.capture.get_focus_absolute().set_value_raw(v)

    property focus_relative:
        def __get__(self): return self.capture.get_focus_relative().get_value_raw()
        def __set__(self, int v): self.capture.get_focus_relative().set_value_raw(v)

    property focus_auto:
        def __get__(self): return self.capture.get_focus_auto().get_value_raw()
        def __set__(self, int v): self.capture.get_focus_auto().set_value_raw(v)

    def set_controller_value(self, bytes name, float value):
        self.capture.get_controller(<char*>name).set_value(value)

    def get_controller_value(self, bytes name):
        return self.capture.get_controller(<char*>name).get_value()

    def grab(self):
        del self.mat
        with nogil:
            self.mat = self.capture.grab()

        return eigenmat_to_numpy(self.mat)

