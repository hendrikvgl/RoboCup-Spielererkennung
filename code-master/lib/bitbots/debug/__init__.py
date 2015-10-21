#-*- coding:utf-8 -*-
from __future__ import print_function
import sys

# Und damit das ganze auch ohne Virtualenv geht (z.B. wenn cross-compiling oder an tools unter
# Windows gearbeitet wird, machen wir hier etwas fehlerbehandlung und dummy
# implementierungen
try:
    # Das wird hier importiert um das Importieren von anderen stellen
    # schöner zu machen, so geht from bitbots.debug import Scope
    from bitbots.debug.debug import Scope
except ImportError as e:

    import traceback
    # the following errors going not to stderr so it is easier to filter them out
    print("\033[1;31m[Debug]", e, "\033[0m", file=sys.stdout)
    print("\033[1;31m[Debug]", traceback.format_exc(), "\033[0m", file=sys.stdout)

    # Wir geben eine Warnung aus das das so nicht geht
    print("\033[1;31m[Warning] WARNING: USE DUMMY DEBUG IMPLEMENTATION\033[0m", file=sys.stdout)
    print("\033[1;31m[Warning] ORIGINAL IMPLEMENTATION NOT FOUND\033[0m", file=sys.stdout)

    class Scope(object):
        def __init__(self, name):

            self.name = name

        def log(self, message, value=None):
            if value is None:
                # kein 2. Parameter: eine logmessage
                print("[%s]: %s" % (self.name, message), file=sys.stderr)
            else:
                # ignorieren wir da sonst Console zugespammt
                # ist normalerweise nur fürs versenden gedacht
                pass

        def __lshift__(self, message):
            self.log(message)

        def warning(self, message):
            print("\033[1;31m[%s.warning]: %s\033[0m" % (self.name, message), file=sys.stderr)

        def sub(self, name):
            return Scope("%s.%s" % (self.name, name))

        def __call__(self, message, value=None):
            self.log(message, value)

        def __reduce__(self):
            """
            Nötig damit debug Pickabel ist.
            Gibt im wesentlichen an wie man das Objekt wieder erstellen kann
            """
            return (Scope, (self.name, ), None, None, None)

        def print_exception(self, e):
            self.warning(str(e))
            self.warning(traceback.format_exc())

        def error(self, e, prefix_msg="", speak=True):
            if speak:
                from bitbots.util.speaker import say
                say(prefix_msg + " " + str(e))
            self.warning(prefix_msg + " " + str(e))
            self.warning(traceback.format_exc())
