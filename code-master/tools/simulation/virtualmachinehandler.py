#!/usr/bin/env python
#-*- coding:utf-8 -*-
# wol.py

import socket
import struct
import os
import time
import psycopg2
import gevent
import subprocess

def wake_on_lan(macaddress):
    """ Switches on remote computers using WOL. """

    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    send_data = ''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data,
                             struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 7))


HOST_DOWN = 0
HOST_BOOTING = 1
HOST_UP = 2

class BaseHost(object):
    def check_online(self):
        if self.ssh_command("exit 0") == 0:
            print self.ip, " is online"
            self.status = HOST_UP
            return True
        else:
            if self.status == HOST_BOOTING:
                print self.ip, " is booting"
                if time.time() - self.start_time > 300:
                    self.status = HOST_DOWN
            else:
                print self.ip, " is down"
                self.status = HOST_DOWN
            return False

    def ssh_command(self, command):
        return subprocess.call(["ssh", "%s@%s" % (self.user, self.ip), command])

    def stop_res(self):
        self.ssh_command("sudo poweroff")

class Host(BaseHost):
    def __init__(self, ID, ip, mac, name):
        self.ip = ip
        self.mac = mac
        self.status = HOST_DOWN
        self.start_time = time.time()
        self.name = name
        self.ID = ID
        self.user = "bitbots"
        print "Test Host %s" % ip
        self.check_online()

    def start_host(self):
        if self.check_online():
            return
        if self.status == HOST_BOOTING:
            return
        wake_on_lan(self.mac)
        print "Wake up %s" % self.name
        self.status = HOST_BOOTING
        self.start_time = time.time()

    def stop_host(self):
        self.stop_res()
        self.status = HOST_DOWN
        print "Shutdown %s" % self.name

    def start_container(self, robot):
        # check if robot is here, else clone
        robot.status = HOST_BOOTING
        self.ssh_command("sudo lxc-start -d -n %s" % robot.name)

    def stop_container(self, robot):
        self.robot.stop_res()
        #todo sleep
        self.ssh_command("sudo lxc-stop -n %s" % robot.name)
        robot.status = HOST_DOWN


class Robot(BaseHost):
    def __init__(self, name, ip, host):
        self.name = name
        self.ip = ip
        self.host = host
        self.status = HOST_DOWN
        self.start_time = time.time()
        self.check_online()
        self.user = "darwin"

    def start(self):
        if self.status == HOST_DOWN:
            self.host.start_container()

SYSTEM_P4 = 1
SYSTEM_OPTI745 = 2

SYSTEM_ANY = SYSTEM_OPTI745 or SYSTEM_OPTI745

class Hosts(object):
    def __init__(self):
        self.con = psycopg2.connect("dbname=simserv user=simserv password=robocup2012 host=simsrv01")
        self.cur = self.con.cursor()
        self.host_stati = {}
        self.hosts = []
        self.cur.execute("SELECT ID, ip, mac, name FROM host;")
        data = self.cur.fetchall()
        for host in data:
            self.hosts.append(Host(host[0], host[1], host[2], host[3]))

    #def get_host(self, unused=True, system_type=SYSTEM_P4

class EventHandler(object):
    def __init__(self):
        self.events = []

    def run(self):
        while True:
            print self.events
            start = time.time()
            for event in self.events[:]:
                if not event.execute(self):
                    self.events.remove(event)
                    if event.next_event:
                        self.events.append(event.next_event)
            gevent.sleep(max(start - time.time() + 5, 0)) #  5 sekunden mindestens

    def add_event(self, event):
        self.events.append(event)


class Event(object):
    def __init__(self, in_sec, res, next_event=None):
        self.in_sec = in_sec
        self.last = -1
        self.res = res
        self.next_event = next_event

    def execute(self, event_handler):
        if self.last == -1:
            self.last = time.time()
        if self.in_sec + self.last < time.time():
            return self.run(event_handler)
        else:
            return True

    def run(self, event_handler):
        return False


class StartHost(Event):
    def run(self, event_handler):
        if self.res.status == HOST_DOWN:
            self.res.start_host()
            return True
        else:
            return not self.res.check_online()

class StopHost(Event):
    def run(self, event_handler):
        self.res.stop_host()
        return False

"""
with cursor(con) as cur:
    cur.execute("update...")

@contextlib.contextmanager
def cursor(con):
    try:
        yield con.cursor()
    finally:
        con.commit()
"""
if __name__ == "__main__":
    """
    switch_of_lan("192.168.230.61") #simhost1
    switch_of_lan("192.168.230.62") #simhost1
    switch_of_lan("192.168.230.63") #simhost1
    switch_of_lan("192.168.230.64") #simhost1
    switch_of_lan("192.168.230.65") #simhost1
    switch_of_lan("192.168.230.66") #simhost1
    #time.sleep(60)"""
    """wake_on_lan("00:30:05:79:cf:e3") #simhost1
    wake_on_lan("00:30:05:79:ce:ef") # simhost2
    wake_on_lan("00:30:05:77:0f:64") # simhost3
    wake_on_lan("00:1a:a0:d2:11:80") # simhost4
    wake_on_lan("00:1a:a0:d2:08:dc") # simhost5 # kaputt
    wake_on_lan("00:1a:a0:d2:19:42") # simhost6 # ungetestet
    """
    eventHandler = EventHandler()
    hosts = Hosts()
    for host in hosts.hosts:
        eventHandler.add_event(
            StartHost(
                20,
                host,
                StopHost(
                    120,
                    host,
                    StartHost(
                        120,
                        host,
                        StopHost(
                            120,
                            host
                        )
                    )
                )
            )
        )

    eventHandler.run()
