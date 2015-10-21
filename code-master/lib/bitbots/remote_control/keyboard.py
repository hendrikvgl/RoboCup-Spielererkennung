#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gevent
import socket
import gevent.socket
import sys
import tty
import termios
import subprocess

class KeyBoardControl(object):
    def __init__(self, debug):
        self.debug = debug
        self.socket = gevent.socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.process = None
        self.connect()
        gevent.spawn(self.listen)

    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            gevent.socket.wait_read(sys.stdin.fileno())
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def listen(self):
        while True:
            print self.socket.recv(100)

    def connect(self):
        while True:
            try:
                print "\n"
                print "Das Walk-Script kann sich zu einem entfernen Roboter verbinden auf dem "
                print "start-demo läuft, oder auf dem lokalen Roboter selbst für die nötige umgebung nutzen"
                ch = raw_input("Lokal Nutzen (J / n)")
                if ch == "J" or ch =="j" or ch == "":
                    ch2 = raw_input("Demo-Verhalten Starten? (j / N)")
                    if ch2 == "j" or ch2 == "J":
                        if self.process is None:
                            print "Starte Demo-Verhalten..."
                            self.process = subprocess.Popen(("start-demo",""), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            gevent.sleep(2)
                    print "Connecte zu Demo-Verhalten"
                    ip = "127.0.0.1"
                else:
                    ip = raw_input("Enter IP of Robot: ")
                self.socket.connect((ip,12345))
                break
            except socket.error:
                print"Error, IP richtig eingegeben??"

    def send(self, data):
        print "Send: %s" % data
        self.socket.send(data)

    def keyboard_control(self):
        try:
            scope = self.debug.sub("Controller")
            scope << "Start"
            print "Roboter bewegen mit 'q(stapfen) w(vorwärts) s(rückw) Leer(Stop)'"
            print "f/g für seitwärts"
            print "Hip Pitch anpassen mit ,/., Kopf bewegen mit 8/u/i/j"
            print "ä Arme Off"
            print "'a(links) d(rechts) k(right_kick) l(left_kick)'"
            print "'y(stand-up back) x(stand-up front) c(hinlegen back) m(kopfstand)'"
            print "'e (hinwerfen links) r (arm hoch links) '"
            print "'t (arm hoch rechts) z (hinwerfen rechts)'"
            print "'p (demo script, muss noch ausgebaut werden)'"
            print "'! (reconnect, auf andere IP Senden)"
            while True:
                ch = self.getch()
                if ch in ("\x03", "\x04"):
                    # Zeichen ist Strg-c oder Strg-d, abbrechen
                    scope << "Exiting"
                    self.send(" ")
                    break
                if ch == "!":
                    self.connect()
                    ch = ""

                if ch  in ("q","w","a","s","d"," ",",",".",'o', 'g','f'):
                    # befehle fürs laufen
                    self.send(ch)
                    print ch

                if ch == "k":
                    self.send("play rk")

                if ch == "l":
                    # Den Ball mit links kicken
                    self.send("play lk")

                if ch == "1":
                    # Den Ball mit links kicken
                    self.send("play pickup")
                if ch == "2":
                    # Den Ball mit links kicken
                    self.send("play throw")
                if ch == "3":
                    # Den Ball mit links kicken
                    self.send("play throwin")

                if ch == "y":
                    # Aufstehen vom Rücken
                    self.send("play bottom-up")

                if ch == "x":
                    # Aufstehen vom Buach
                    self.send("play front-up")

                if ch == "r":
                    self.send("play goalie_left_shoulder")

                if ch == "e":
                    self.send("play goalie_left2")
                if ch == "t":
                    self.send("play goalie_right_shoulder")
                if ch == "g":
                    pass
                    #self.send("play goalie_grund2")

                if ch == "z":
                    self.send("play goalie_right3")

                if ch == "c":
                    # Auf den Rücken legen
                    self.send("play lie-up")

                if ch == "m":
                    #kopfstand
                    self.send("play headstand_new_head")

                if ch in "8uij":
                    #befehle für den Kopf
                    self.send(ch)
                """
                if ch == "p":
                    self.send("play lie-up")
                    gevent.sleep(10)
                    self.send("play bottom-up")
                    gevent.sleep(10)
                    self.send("play headstand_new_head")
                    gevent.sleep(16)
                    self.send("w")
                    gevent.sleep(4)
                    self.send(" ")
                """
                # Infos ausgeben
        finally:
            if type(self.process) != type(None):
                scope << "Beende Demo verhalten"
                self.process.terminate()
