#-*- coding:utf-8 -*-
"""
EventFramework
^^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>


Das EventFramework handelt events innerhalb der Modularchitektur des
normalen Frameworks. Events sind nur für seltenere vorkomnise wie
z.B. Penalty gedacht, insbesondere sollen nicht jedes Frame.

Alle Events für die Modularchitektur sind in :mod:`bitbots.modules.events`
definiert

History:

* 8.1.13: Created (Nils Rokita)

"""


class EventFramework(object):
    """
    Diese Klasse Kümmert sich um das Dispatchen von Events
    """
    def __init__(self, debug):
        self.debug = debug.sub("EventFramework")
        self.events = {}
        self.event_qeue = []

    def register_to_event(self, event, function):
        """
        Registriert function auf das Event event. Diese Funktion muss
        ein Argument entgegennehmen, welches je nach Event daten beinhaltet.

        .. hint:: Die Registrierte Funktion kann je nach event sender,
                  in einem eigenen Thread ausgeführt werden.

        """
        if not event in self.events:
            self.events[event] = []
        self.events[event].append(function)
        self.debug("Register {} to Event {}".format(function, event))

    def unregister_from_event(self, event, function):
        """
        Hebt die Registrierung der Funktion für das event auf.
        """
        self.events[event].delete(function)

    def send_event(self, event, data=None):
        """
        Sendet das Event event zu allen die sich dafür registriert haben

        .. warning:: Nicht in einem AbstractProcessModule verwenden, das
            ist momentan noch nicht unterstützt.
        """
        self.event_qeue.append((event, data))
        self.debug("Event {}".format(event))
        while len(self.event_qeue):
            event, data = self.event_qeue.pop(0)
            if event in self.events:
                for func in self.events[event]:
                    func(data)

