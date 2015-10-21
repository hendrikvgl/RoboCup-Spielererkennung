#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
GameStateReceiver
^^^^^^^^^^^^^^^^^

Dieses Modul Kann auch stand-alone zum ansehen der Gamecontroler
Daten verwendet werden..
    python lib/darwin/game/reciever.py

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* ~1.4.12: Created (Nils Rokita)

* 11.7.12: Timeouts (Nils Rokita)

* 24.4.13: Antworten an den Gamecontoller korregiert

* 31.12.13: Zeit seit letztem empfangenen Packet

* 02.03.14: Neues Packetformat implementiert

"""


import socket
import time
from construct import Container, ConstError
from bitbots.game.gamestate import GameState, ReturnData

from bitbots.debug.debug import Scope
debug = Scope("GameController")

class GameStateReceiver(object):
    '''
    Diese Klasse stellt einen einfachen UDP Server zur Verfügung. Dem
    Konstruktor wird mit *addr* die Adresse übergeben, auf der auf
    UDP Broadcast-Pakete gewartet werden soll.

    Wird ein Paket empfangen, wird es als GameState-Datenstruktur interpretiert
    und an die funktion :func:`on_new_gamestate` übergeben.
    Diese sollte in einer sinnvollen Implementierung dann etwas mit dem
    aktuellen GameState unternehmen (z.B. das Verhalten berechnen).

    Einfaches Beispiel zur Verwendung dieser Klasse::

        rec = GameDataReceiver()
        rec.on_new_gamestate = handle_new_gamestate
        rec.receive_forever()

    '''
    __slots__ = ['socket', 'addr', 'state', 'running','team','player','time',
                'man_penalize', 'socket2']

    def __init__(self, team=12, player=1, addr=('0.0.0.0', 3838)):
        self.state = None
        self.socket = None
        self.addr = (addr[0], int(addr[1]))
        self.running = True
        self.team = team
        self.player = player
        self._open_socket()
        self.man_penalize = False
        self.time = time.time()+10000  # so gibts nur wenn mal etwas
        # empfangen wurde nachrichten das es verloren wurde

    def _open_socket(self):
        ''' Erzeugt das Socket '''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.settimeout(0.5)
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def receive_forever(self):
        ''' Wartet in einer Schleife auf GameState-Pakete, bis die
            Methode :func:`stop` aufgerufen wird.
        '''
        while self.running:
            try:
                self.receive_once()
            except IOError as e:
                debug.log("Fehler beim Senden des KeepAlive: " + str(e))

    def receive_once(self):
        """ Empfängt ein Paket und interpretiert es. Danach wird die
            :func:`on_new_gamestate`-Methode mit den interpretierten
            Daten aufgerufen und eine Antwort gesendet
        """
        try:
            data, peer = self.socket.recvfrom(GameState.sizeof())
            self.state = GameState.parse(data)
            self.on_new_gamestate(self.state)
            self.time = time.time()
            self.send_once(peer)
        except socket.timeout:
            self.state = None
        except ConstError:
            # ein altes gamestatepacket erhalten
            if self.state is None:
                debug.warning("GameController: Empfange nur Veraltete Packete!")
        except Exception as e:
            debug.error(e)
            pass #fehler biem empfangen, meist einfach nur nen falsches packet

    def send_once(self, peer):
        """ Sendet ein Lebenszeichen zum GameController """
        retmsg = 2 if not self.man_penalize else 0
        data = Container(
            header="RGrt",
            version=2,
            team=self.team,
            player=self.player,
            message=retmsg)
        try:
            self.socket.sendto(ReturnData.build(data), (peer[0], 3838))
        except Exception as e:
            debug.log("Network Error: %s" % str(e))

    def on_new_gamestate(self, state):
        ''' Wird aufgerufen, wenn ein neuer GameState empfangen wurde '''
        pass

    def get_last_state(self):
        ''' Gibt den letzten empfangen GameState zurück '''
        return self.state

    def get_last_time(self):
        """Gibt die zeit des letzten empfangenen Status zurück"""
        return self.time

    def get_time_since_last(self):
        """Gibt die zeit seit dem Letzten empfangenen Packet zurück"""
        return time.time() - self.time

    def stop(self):
        ''' Stoppt :func:`serve_forever`. '''
        self.running = False

    def set_manual_penalty(self, flag):
        self.man_penalize = flag


class GameStateReceiver2(GameStateReceiver):
        def on_new_gamestate(self, state):
            #print(state)
            for team in state.teams:
                print("Team: ", team.team_number)
                print("Goals: ", team.score)
                i = 0
                for player in team.players:
                    print("Player %02d: Penalty: %02d Time: %d" % (
                        i,
                        player.penalty,
                        player.secs_till_unpenalised))
                    i+=1


def main():

    rec = GameStateReceiver2()
    rec.receive_forever()

if __name__ == '__main__':
    main()

