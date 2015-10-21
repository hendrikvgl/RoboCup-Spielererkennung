#-*- coding:utf-8 -*-
"""
Events
^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 9.1.14: Created (Nils Rokita)

Hier sind alle Events die es gibt aufgeführt
"""


# GamecontrollerModule
EVENT_PENALTY="Penalty"
""" Dieses Event wird gefeuert wenn der Roboter eine Penalty bekommen hatt"""
EVENT_NO_PENALTY="No Penalty"
""" Dieses Event ist dafür wenn der Roboter den Penalty zustand verlässt"""
EVENT_GAME_STATUS_CHANGED="New Gamestatus"
""" Dieses Event wird bei änderungen des Gamestatus gefeuert, als
kommt der Aktuelle Status mit"""

# Manual Penalty
EVENT_MANUAL_PENALTY="Manual Penalty"
""" Dieses Event wird beim Maunellen Penelizen gesendet"""
EVENT_NO_MANUAL_PENALTY="No Manual Penalty"
""" Dieses Event wird beim Manuelen unpenelizen Gesendet"""

# StackMachineModule
EVENT_GLOBAL_INTERRUPT="GlobalInterrupt"
"""Auf dieses Event hin werden alle Stackmachins einen Interrupt
durchführen. Daten: Ein Name wo der interrupt herkommt."""

# ButtonModule
EVENT_BUTTON1_UP="Button1_Up"
"""Button1 released"""
EVENT_BUTTON1_DOWN="Button1_Down"
"""Button1 pressed"""
EVENT_BUTTON2_UP="Button2_Up"
"""Button2 released"""
EVENT_BUTTON2_DOWN="Button2_Down"
"""Button2 pressed"""

EVENT_MANUAL_START="manualstart"
"""Spiel soll manuell starten (20 sec deleay)"""

EVENT_GOAL="goal"
"""Es ist ein Tor für uns gefallen"""
