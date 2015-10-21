#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
Urwid-Widgets für das Record-UI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Timon Giese <timon.giese@bit-bots.de>

History:
--------

    * 2014-01-17: Modul angelegt, Klassen aus der ui.py gezogen, wo nur das
      Hauptfenster verbleiben soll.

"""
import logging
from bitbots.debug import Scope


class ConsoleHandler(logging.Handler):
    """ Stinknormaler Python Logging Handler,
    der nachrichten für die Konsole auffängt und dort anzeigt


    .. codeauthor:: Timon Giese <timon.giese@bit-bots.de>

    """

    def __init__(self, console):
        self.console = console
        super(ConsoleHandler, self).__init__()

    def emit(self, record):
        if record.levelno > 40:
            fmt = ('critical', record.message)
        elif record.levelno > 30:
            fmt = ('error', record.message)
        elif record.levelno > 20:
            fmt = ('warning', record.message)
        elif record.levelno <= 10:
            fmt = ('debug', record.message)
        else:
            fmt = record.message

        self.console.write(fmt)


class DarwinDebugHandler(logging.StreamHandler):
    """ Debug-Handler that passes Messages to the darwin debugging
    """
    def __init__(self):
        self.glog = Scope("bin.Record", console_out=False)  # global logger
        super(DarwinDebugHandler, self).__init__(self)
        self.setLevel(logging.DEBUG)
        self.glog.log("Logging attached to Record-Script")
        if not __debug__:
            self.glog.warning("__debug__ is false, some messages might be optimised into nirvana!")

    def write(self, message):
        """ Called by logger
        Implements an function required by Objects attached to a
        :class:`StreamHandler`
        :param message: Incoming Logging Message
        :type message: Should be a String
        :return: Nothing
        """
        self.glog.log(message)

    def flush(self):
        """ Called by logger
        Implements an function required by Objects attached to a
        :class:`StreamHandler`
        (This one actually does nothing, it is only here for the looks)
        :return: Nothing
        """
        pass
