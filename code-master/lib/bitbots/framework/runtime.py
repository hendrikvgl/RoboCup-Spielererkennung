#-*- coding:utf-8 -*-
"""
ModuleFramework
^^^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 1.1.12: Erstellt, irgendwann mal (Olli)
* 8.1.13: In eigene Datei verschoben (Nils Rokita)

"""

from time import time
from gevent import sleep
import multiprocessing
import sys

from bitbots.framework.module_service import ModuleService
from bitbots.framework.event_framework import EventFramework
from bitbots.debug import Scope
from bitbots.modules.keys import DATA_KEY_DATA_CAMERA
from bitbots.util.speaker import to_speak


def do_import(name):
    """ Importiert ein Modul und gibt eine Referenz darauf zurück """
    __import__(name)
    return sys.modules[name]


class Runtime(object):
    """
    This class handles the load of modules by calling
    the :func:`load` method.
    By executing the :func:`run` method it cycles throught the update
    methods of all loaded modules.
    """
    def __init__(self, debug=None):
        self.debug = debug or Scope("ModuleRuntime")
        self.service = ModuleService(self.debug)
        self.event_framework = EventFramework(self.debug)

    def load(self, name):
        """ This method loads a module by a given name a calls
        the :func:`register` method of the module."""
        try:
            module = do_import(name)
            if not hasattr(module, "register") or \
                not callable(module.register):
                self.debug.warning(
                "Warnung, Modul '%s' hat keine Funktion 'register'" %
                name)
                return

            module.register(self.service)
        except Exception, e:
            self.debug.error(e,  "Fehler in Modul %s:" % (str(name)))

    def run(self, names):
        """
        This method firstly resolves the module dependencies and
        instanciate one object per module. After that it creates the
        empty data Dictionary in the first place and cylcles in a
        while-loop through the update methods of all present modules
        """
        names = self.service.resolve(names)
        modules = self.service.instantiate(names)

        modules_pre = []
        modules_update = []
        modules_post = []
        for module in modules:
            for clazz in module.__class__.__mro__:
                if clazz.__name__ != 'AbstractModule':
                    if "pre" in clazz.__dict__ and \
                            module not in modules_pre:
                        modules_pre.append(module)

                    if "update" in clazz.__dict__ and \
                            module not in modules_update:
                        modules_update.append(module)

                    if "post" in clazz.__dict__ and \
                            module not in modules_post:
                        modules_post.append(module)

                else:
                    break

        try:
            runs = 0
            last_run = time()
            last_debug = time()
            data = {}

            if "--simulate" in sys.argv:
                self.debug("Simulation Mode")
                data["Simulation"] = True

            if "--datacamera" in sys.argv:
                self.debug("Data Camera aktivated")
                data[DATA_KEY_DATA_CAMERA] = True
                images = []
                print sys.argv, sys.argv[2:]
                for image in sys.argv[2:]:
                    if not image[0] == "-":
                        images.append(image)
                data["ImagePaths"] = images
                data["Buffer"] = True if "--buffer" in sys.argv else False

            #internal_init einzelner Module aufruffen
            module_debug = Scope("Module")
            for mod in modules:
                mod.internal_init(module_debug, self.event_framework)

            #startmethoden einzelner Module aufruffen
            for mod in modules:
                mod.start(data)

            while True:
                # Zeitberechnung.. Es sind dt Sekunden vergangen seit
                #  dem letzten Durchlauf
                now = time()
                dt, last_run = now - last_run, now
                data["dt"] = dt

                # Module aufrufen
                for mod in modules_pre:
                    mod.pre(data)

                for mod in modules_update:
                    mod.update(data)

                for mod in modules_post:
                    mod.post(data)

                # Debug Informationen alle zwei Sekunden posten
                runs += 1
                if now - last_debug > 2:
                    self.debug.log("Iterations/Second",
                        runs / (now - last_debug))
                    last_debug = now
                    runs = 0

                # Auf 50 Durchläufe pro Sekunde beschränken
                now = time()
                if now - last_run < 0.02:
                    sleep(0.02 - (now - last_run))


        except BaseException as e:
            #BaseException da sonst ein SystemExit nicht gefangen wird
            for process in multiprocessing.active_children():
                try:
                    self.debug.log("Kille Subprocess %s" % process.name)
                    process.terminate()
                except Exception as e2:
                    self.debug.warning(e2, "Fehler beim beenden vom Subprozess")
                    # beim beenden von subprozessen fehler ignorieren
                    pass
            if  isinstance(e, KeyboardInterrupt):
                # Keybord interrupt ist meist schon absicht...
                raise
            self.debug.error(e, "Fehler in Modul %s:" %
                (str(mod)))
            self.debug.log("Framework: SystemExit")
            i = 0
            while i < 120 and to_speak():
                self.debug.log("Wait for espeak to read messages (%d messages, %d/120 trys)" % (to_speak(), i))
                sleep(0.5)
                i += 1
            raise SystemExit("Fehler in Modul %s: %s" %
                (str(mod), str(e)))
