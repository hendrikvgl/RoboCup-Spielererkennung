# -*- coding:utf-8 -*-
"""
TestBehaviourModule
^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Martin Poppinga <1popping@informatik.uni-hamburg.de>

History:
* 5.3.13: Created (Martin Poppinga)
"""
import importlib

from bitbots.modules.abstract.stack_machine_module import StackMachineModule
from bitbots.modules.keys import DATA_KEY_PENALTY


module = None  # Soll vom startscript überschrieben werden


class TestBehaviourModule(StackMachineModule):
    """
    Läd eine bestimmtes Element auf den Stack für Testzwecke
    """

    def __init__(self):
        modulename = module.split(".")[-1]

        print "Starte:\n " + modulename + " in " + "bitbots.modules.behaviour." + module
        startmodule = importlib.import_module("bitbots.modules.behaviour." + module, modulename)
        self.set_start_module(getattr(startmodule, modulename))


def register(ms):
    ms.add(TestBehaviourModule, "TestBehaviourModule",
           requires=["Ipc", "BallInfo", "Pose", "BallFound", "OwnKickOff", DATA_KEY_PENALTY, "Walking"],
           provides=["Duty"])