ServoTool
*********

Das ServoTool ist von den Darmstädtern geschrieben und erlaubt die komplette
Modifikation des EEPROM eines DYNAMIXELs mit oder ohne Darwin. Es kann auf zwei
sinnvolle Weisen genutzt werden. Entweder durch das Anschließen einzelner
DYNAMIXEL-Motoren (oder diese in Reihe geschaltet) via
:doc:`USB2DXL-Adapter </hardware/teile/motor/usb2dxl>` an den eigenen PC, oder
man startet das Tool direkt über den Darwin.

.. note::

    Das Modifizieren der Werte über einen
    :doc:`USB2DXL-Adapter </hardware/teile/motor/usb2dxl>` an einen Darwin mit
    laufender Motion angeschlossen, führt zur Kollision zwischen dem
    :doc:`CM-730 Board </hardware/teile/cm730>` und RS-485 Bus (Laptop).

Es liegt in Git unter *tools/servotool/*.



Installation
============

Für das Anschließen via USB2DXL-Adapter
---------------------------------------

Vorausgesetzt wird die Python Version der *Qwt5 technical widget library*::

    $ sudo apt-get install python-serial python-qwt5-qt4



Für die Benutzung über den Darwin
---------------------------------

Damit die GUI des Tools über den Darwin an unseren PC per :program:`ssh`
gesendet wird, benutzen wir *X11-Forwarding*. Dafür muss neben der *Qwt5
technical widget library* auch das Packet *xauth* vorhanden sein::

    $ sudo apt-get install python-serial python-qwt5-qt4 xauth

Außerdem muss dem SSH-Daemon des Servers mitgeteilt werden, dass *X-Forwarding*
verwendet wird. Das wird über die Konfigurationsdatei */etc/ssh/sshd_config*
erledigt. Dort wird die Option
::

    X11Forwarding yes

gesetzt. Danach ist ein Neustart des Daemons erforderlich.

Zusätzlich müssen in der Client-Konfigurationsdatei */etc/ssh/ssh_config* die
Einträge
::

    ForwardX11 yes

und
::

    ForwardX11Trusted yes

einkommentiert werden.

Außerdem muss natürlich das Tool auf dem Darwin vorhanden sein. Ist es nicht der
Fall, so kopiert man das Verzeichnis auf den Darwin::

   $ scp -r servotool bitbots@XXX.XXX.XXX.XX:servotool



Ausführen
=========



Für das Anschließen via USB2DXL-Adapter
---------------------------------------

Um das Tool zu starten, führt man im oben genannten Verzeichnis
:command:`python src/ServoTool.py` aus.



Für die Benutzung über den Darwin
---------------------------------

Zuerst muss eine Verbindung aufgebaut werden und das *X11-Forwarding* aktiviert
werden::

    $ ssh -X bitbots@XXX.XXX.XXX.XX

Steht die Verbindung, so braucht man nur
:command:`python servotool/src/ServoTool.py` auszuführen, wonach eine graphische
Oberfläche auf dem Bildschirm erscheint.

Nach dem Auslesen der Daten (*Read All*) sollte ein einziger "Motor" zu sehen
sein. Dies ist das :doc:`CM-730 Board </hardware/teile/cm730>`. Nun muss die
Motorpower aktiviert werden. Dies geschieht durch das Setzen des Parameters
*TorqueEnable* auf 1. Führt man jetzt erneut einen *Scan* aus, so werden alle
Motoren angezeigt.



.. _Benutzung des ServoTools:

Benutzung
=========

Gesetzt werden kann das Protokoll, der Anschluss (-port) und die Baudrate. Wir
verwenden für das Protokoll *RobotisServo*, für den Anschluss */dev/ttyUSB0* und
als Baudrate *1000000*, denn diese wird hier als Target BPS übergeben und
entspricht dem Datenwert *1*.

.. note::
    Der Datenwert 34 entspricht dem Target BPS 57600.

Der *Read All*-Button sorgt für das Scannen und Datenauslesen der Daten, wonach
diese in der Tabelle angezeigt werden.

Die *Scan*-Buttons prüfen, ob und welche Motoren angesprochen werden können.
Diese werden in der Tabelle angezeigt, aber nicht mit Daten ausgefüllt.

Zusätzlich können einzelne Motoren über ihre IDs gesucht werden, in dem man
diese mit dem *Ping*-Button ein Packet sendet. Über den *Read*-Button können die
Daten ausgelesen werden.

Durch das Ändern des Loglevels können mehr oder weniger Informationen in der
Konsole ausgegeben werden.



Modifikation der Datenwerte
===========================

Jeder Wert kann beliebig geändert werden, egal ob es sinnvoll ist oder nicht.
Dies geschieht durch das Anklicken des Feldes und das Eintippen des gewünschten
Wertes als ganze Zahl. So kann sinnvollerweise die Baudrate und Motor-ID gesetzt
werden, aber auch sinnloserweise die Firmwareversion, Modelnummer etc.
