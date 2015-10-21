=====================
Miscallaneous Scripts
=====================

.. todo:: Aufteilen auf Darwin und Externe scripte, dann jeweilgen sektionen zuordnen

*****
color
*****

Setzt die LED-Farben des Darwins.
Usage siehe::

  color --help
  color [subcommand] --help

Config
------

===========  ===============================================================================
EyesOff      muss auf False stehen damit Augenfarben geändert werden können
EyesPenalty  Wenn True, blinken die Augen bei penalized state - auch wenn EyesOff False ist
===========  ===============================================================================

Examples
--------

::

  color eyes str Lime
  color forehead rgb 255 0 0

.. note::

  Ein Motion-Server muss laufen damit werte im CM-730 EEPROM geändert werden können.
  So auch für das ändern der Augenfarbe.

***********
pseudo-heat
***********

Sendet zufällige debug-daten die die Temperautur der Motoren angeben

***********
pseudo-volt
***********

Sendet zufällige debug-daten die die Voltage der Motoren angeben

***********
dummy-debug
***********

Sendet zufällige Debug-Daten zu Voltage, Temeratur und Error-Bits


******
Motors
******

Wenn man motors eingibt wird einem eine ASCII-Art eines Darwins mit den Motornummern angezeigt.