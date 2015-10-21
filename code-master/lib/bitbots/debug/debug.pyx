from cython.operator cimport dereference as deref
import traceback


cdef class Scope:
    def __cinit__(self, name, console_out = True):
        if isinstance(name, unicode):
            name = name.encode("utf8")

        self.name = name
        self.console_out = console_out
        self.scope = new CScope(name, console_out)

    def __dealloc__(self):
        del self.scope

    def __lshift__(self, other):
        self.log(other)

    def __call__(self, *args):
        self.log(*args)

    def __bool__(self):
        return self.scope.to_bool()

    def __reduce__(self):
        """
        Nötig damit debug Pickabel ist.
        Gibt im wesentlichen an wie man das Objekt wieder erstellen kann
        """
        return (Scope, (self.name, ), None, None, None)

    def get_name(self):
        return self.name

    def get_console_out(self):
        return self.console_out

    cpdef Scope sub(self, name, console_out = True):
        return Scope(self.name + "." + name, console_out)

    def warning(self, text):
        cdef bytes msg = text
        self.scope.warning(self.name, <char*>msg)

    def log(self, first_, *more):
        cdef bytes first
        if isinstance(first_, bytes):
            first = first_

        elif isinstance(first_, unicode):
            first = (<unicode>first_).encode("utf8")

        else:
            raise ValueError("First argument must be bytes or unicode")

        if len(more) == 0:
            deref(self.scope) << <char*>first;
            return

        if len(more) != 1:
            raise ValueError("One or two arguments only")

        cdef bytes name = first
        cdef object value = more[0]
        if isinstance(value, (int, long)):
            self.scope.log(<char*>name, <int?>value)
            return

        if isinstance(value, float):
            if value < 1e+7:
                self.scope.log(<char*>name, <float>value)
            else:
                self.scope.log(<char*>name, <double>value)
            return

        if isinstance(value, bytes):
            self.scope.log(<char*>name, string(<char*><bytes>value, len(value)))
            return

        if isinstance(value, unicode):
            value = (<unicode>value).encode("utf8")
            self.scope.log(<char*>name, string(<char*><bytes>value, len(value)))
            return

        # Geht nicht!
        raise ValueError("You can not log a variable of this type")

    def print_exception(self, e):
        # TODO: wird das irgendwo verwendet?
        self.warning(str(e))
        self.warning(traceback.format_exc())

    def error(self, e, prefix_msg="", speak=True):
        e_type = str(type(e)).split('.')[-1][:-2]
        if speak:
            from bitbots.util.speaker import say
            say("%s %s: %s" % (prefix_msg, e_type, str(e)))
        self.warning("%s %s: %s" % (prefix_msg, e_type, str(e)))
        self.warning(traceback.format_exc())

