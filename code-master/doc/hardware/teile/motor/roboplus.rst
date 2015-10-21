RoboPlus
********

RoboPlus ist ein Programm von Robotis, dass viele interessante Möglichkeiten für
unsere Darwins bietet, wenn man es geschafft hat, es zum Laufen zu bringen.



Installieren
============

Das Programm ist in unserem Labor schon auf dem Rechner mit Windows 7
installiert. Man braucht zwingenderweise Windows, um es zu installieren (am
besten ein aktuelles, z.B. Windows 7 oder Windows 8). Es kann aus dem Internet
heruntergeladen werden (ein paar hundert MB groß – dazu einfach RoboPlus
googeln). Ansonsten entspricht der Installer dem ganz normalen Windows Standard.



Benutzung
=========

Das Programm besteht eigentlich aus mehreren Unterprogrammen. Am
interessantesten ist der DynamixelWizard.



DynamixelWizard
---------------

Hiermit lassen sich alle Werte der Motoren auslesen und setzen. Vor allem aber
ist dies die einzige Möglichkeit, die aktuelle Firmware auf die Motoren zu
spielen.



Auf Motoren zugreifen
---------------------

Die Motoren werden mit dem :program:`USB2Dynamixel` angeschlossen
(:doc:`siehe Doku </hardware/teile/motor/usb2dxl>`). Oben in der Leiste den
COM-Port auswählen (meistens *COM3*) und auf den Button rechts davon klicken, um
sich zu verbinden. Nun müsste man die Baudraten, auf denen man suchen möchte,
angeben können. Normalerweise braucht man nur *1* und *34* (normale Suche). Wenn
man auf Suchen klickt, sieht man irgendwann links die Motoren auftauchen.
Sollten keine Motoren auftauchen -> Verkabelung und Motorstrom überprüfen
(:doc:`siehe Doku </hardware/teile/motor/usb2dxl>`). Wenn alle Motoren gefunden
wurden, die man gesucht hat, kann man die Suche auch abbrechen. Nun kann man
links die Motoren anwählen, die man braucht. In der Mitte erscheint dann ein
Fenster mit den Werten. Der Rest ist selbsterklärend.



.. _Motor-Firmware updaten:

Firmware updaten
----------------

Wenn man, wie oben beschrieben, die Motoren gefunden hat, kann man oben in der
Leiste auf *Firmware updaten* klicken, um die aktuellste Version der Firmware
auf die momentan **GEFUNDENEN** (nicht unbedingt gleich mit verbundenen) Motoren
zu spielen.

.. warning::
	Niemals mehr als 7 Motoren gleichzeitig vom Wizard updaten lassen, da es
	sonst zu einem Crash kommt! Wenn man hardwareseitig keine Trennung vornehmen
	kann, einfach immer 7 Motoren auf die 34 Baudrate packen und einen neuen
	Suchlauf nur auf der 34 machen, damit er nur 7 findet.



.. _RoboPlus Fehlerbehandlung:

Fehlerbehandlung
----------------



COM-Port in Gebrauch
''''''''''''''''''''

Falls das Programm behauptet, ein COM-Port wäre in Gebrauch, dann einfach das
USB-Kabel ab- und wieder anstecken. Danach sollte das Problem behoben sein.

Sonst hilft es sicherlich schreiend im Kreis zu rennen und die Software zu
verfluchen ...



Motor wird auf Baudrate 1 und 34 nicht gefunden
'''''''''''''''''''''''''''''''''''''''''''''''

* Sichergehen, dass alles wirklich korrekt angeschlossen ist
* Die andere Anschlussmöglichkeit des USB2DXL-Tools austesten
* Versuchen den Motor über den Roboter mit dem :program:`dxl_monitor` zu finden

Wenn das alles nicht funktioniert hat, kann man einen Gesamt-Suchlauf
machen, er alle Baudraten durchsucht, dies dauert allerdings sehr lange.
Außerdem gibt es noch die Möglichkeit zur Firmwarewiederherstellung.
Dazu oben in der Leiste auf *Firmware wiederherstellen* klicken und den
Befehlen folgen. Im Zweifelsfalle ist der Ansprechpartner Marc 0bestman.



Es gibt merkwürdige Fehlermeldungen und Erscheinungen links beim Suchen
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Wahrscheinlich sendet irgendetwas Pakete. Sicherstellen, dass der Roboter nichts
mehr tut (:command:`killall screen`, :command:`killall python` ...).
