#-*- coding:utf-8 -*-
"""
ConfigLoader
^^^^^^^^^^^^

This module provides the :mod:`bitbots.ipc.ipc.sharedMemoryIPC` and the pose


History:
''''''''

* ??.??.??: Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""
from bitbots.ipc import SharedMemoryIPC
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_POSE, DATA_KEY_IPC

class IPCModule(AbstractModule):
    def __init__(self):
        self.ipc = SharedMemoryIPC()

    def start(self, data):
        data[DATA_KEY_IPC] = self.ipc

    def update(self, data):
        data[DATA_KEY_POSE] = self.ipc.get_pose()


def register(ms):

    ms.add(IPCModule, "IPC",
           requires=[],
           provides=[DATA_KEY_IPC, DATA_KEY_POSE])
