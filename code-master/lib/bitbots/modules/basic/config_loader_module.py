#-*- coding:utf-8 -*-
"""
ConfigLoader
^^^^^^^^^^^^

This module provides the config


History:
''''''''

* ??.??.??: Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_CONFIG
from bitbots.util import get_config


class ConfigLoaderModule(AbstractModule):
    """
    This module works just in :func:`__init__` and :func:`start` because the config doesnt change at runtime and is
    just loaded one time. In :func:`start` is the config written in the data dictonary.
    """
    def __init__(self):
        self.config = get_config()

    def start(self, data):
        data[DATA_KEY_CONFIG] = self.config


def register(ms):

    ms.add(ConfigLoaderModule, "ConfigLoader",
           requires=[],
           provides=[DATA_KEY_CONFIG])
