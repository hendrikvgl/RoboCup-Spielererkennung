#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
remoteControl
^^^^^^^^^^^^^^^^^^^^
mit hilfe des remoteControlModule aus dem package bitbots.modules,basic.remote_control_module wird der Roboter fern-
gesteuert, es baut eine UDP Verbindung zu dem auf dem Roboter (hoffentlich) laufenden Demomode und übergiebt dann dem
eigentlichen RemoteControl

Wenn die devices nicht erkannt werden muss folgende Datei (mit Sudo) erstellt werden:
/etc/udev/rules.d/50-remoteControl.rules

KERNEL=="mouse?", OWNER="darwin", MODE="600"
KERNEL=="mice", OWNER="darwin", MODE="600"
KERNEL=="event?", OWNER="darwin", MODE="600"


"""

from bitbots.modules.basic.remote_control_module import PCRemoteControlModule
import gevent
import socket
import gevent.socket


class remoteControl(object):
    def __init__(self):
        self.remote = None

    def connect(self):
        ssocket = gevent.socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        process = None
        while True:
            ip = raw_input("Enter IP of Robot: ")
            try:
                ssocket.connect((ip,12345))
                gevent.sleep(2)
                break
            except socket.error:
                print"Error beim Verbinden, Falsche IP? Alternativ starte bitte das demo-Verhalten auf dem Roboter"
        self.remote = PCRemoteControlModule(ssocket)

    def start(self):
        self.remote.start()

contr = remoteControl()
contr.connect()
contr.start()