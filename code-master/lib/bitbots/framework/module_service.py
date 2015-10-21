#-*- coding:utf-8 -*-
"""
ModuleService
^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 1.1.12: Erstellt, irgendwann mal (Olli)
* 8.1.14: In eigene Datei verschoben (Nils Rokita)

Der Modulservice löst die Abhängigkeiten zwischen den verschiedenen
Modulen der Modul-Architektur auf.

"""

class Description(object):
    """
    Die Repräsentation eines Modules
    """
    def __init__(self, name, clazz, requires, provides):
        self.name = name
        self.clazz = clazz
        self.requires = requires
        self.provides = provides


class ModuleService(object):
    """
    Diese Klasse ist für das handling der verschiedenen Module zuständig.
    Mit ihr lassen sich Zu den Geforderten Modulen alle abhängigkeiten
    auflösen und eine ablaufreihnfolge erstellen
    """
    def __init__(self, debug):
        self.modules = {}
        self.debug = debug

    def add(self, clazz, name, requires=(), provides=()):
        """
        Fügt eine Klasse der liste der bekannten Module hinzu

        :param clazz: DIe Klasse die hinzugefügt wird
        :type clazz: class
        :param name: Der Name des Moduls
        :type name: String
        :param requires: Alle requires dieser Klasse
        :type requires: Tupel
        :param provides: Alle Provides dieser Klasse
        :type provides: Tupel
        """
        desc = Description(name, clazz, requires, provides)
        self.modules[name] = desc

    def get_requires(self, name):
        """
        Gibt die Requires des Modules ´name´ zurück

        :param name: Der Name der Klasse
        :type name: String
        """
        return self.modules[name].requires

    def get_providers(self, what):
        """
        Gibt die Namen aller  Provider für ´what´ zurück.

        :param what: Attribute welches gesucht wird.
        :type what: String
        :return: Namen aller Module die ´wath´ providen
        :returntype: List of Strings
        """
        result = []
        for desc in self.modules.itervalues():
            if what in desc.provides:
                result.append(desc.name)

        return result

    def get_classes(self, names):
        """
        Gibt eine Liste aller bekannten Module zurück die in der liste
        ´names´ sind
        """
        return [self.modules[name].clazz for name in names]

    def instantiate(self, names):
        """
        Instanziert die einzelnen Klassen der Module.
        """
        try:
            return [self.modules[name].clazz() for name in names]
        except Exception as e:
            self.debug.error(e, "Fehler beim instanzieren eines Modules")

    def resolve(self, modules):
        """
        Löst die Abhängikeiten auf und erstellt einen ablaufplan
        """
        result = []
        while modules:
            name = modules.pop(0)
            if name in result:
                continue

            # Suche Module für die Abhängigkeiten
            deps = []
            try:
                for req in self.modules[name].requires:
                    provs = self.get_providers(req)
                    if name in provs:
                        provs.remove(name)

                    if not provs:
                        msg = "Kein Provider für '%s', gefordert von '%s'" % \
                            (req, name)
                        self.debug.warning(msg)
                        raise ValueError(msg)

                    if len(provs) != 1:
                        self.debug.warning(
                            "Achtung, mehrere Provider für '%s': %s" %
                            (req, str(provs)))

                    deps.append(provs[0])

                if all(d in result for d in deps):
                    # Es sind bereits alle Abhängigkeiten vorhanden, wir
                    # merken nehmen dieses Modul ins Ergebnis auf.
                    result.append(name)
                else:
                    # Es müssen erst noch die Abhängigkeiten
                    # abgearbeitet werden
                    if modules.count(name) > 100:
                        # wenn der Name mehr als 100 mal in den
                        # abhänkikeiten ist ist ein Zyklus sehr
                        # wahrscheinlich
                        self.debug.warning("Zyklische abhängikeit in modulen")
                        self.debug("deps: %s name: %s modules: %s" % (deps, name, modules))
                        raise ValueError("Zyklische abhängigkeit")
                    modules = deps + [name] + list(modules)
            except KeyError as e:
                self.debug.error(e,
                    "Modul %s is not in the list off modules." % e)
                raise KeyError("Modul %s nicht gefunden" % e)
        return result
