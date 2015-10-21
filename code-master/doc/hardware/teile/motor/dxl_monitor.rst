Dynamixel Monitor
*****************

Der Dynamixel-Monitor wird auf dem Darwin ausgeführt.

.. note::
    Seit Kurzem können wir auch das ServoTool von den Darmstädtern benutzen,
    das läuft aber nicht auf dem Darwin, sondern über den
    :doc:`USB2DXL-Adapter </hardware/teile/motor/usb2dxl>`.
    Die Firmware kann man damit wohl auch nicht upgraden, aber insgesamt ist
    die Software von den Darmstädtern besser als der Mist, der jetzt folgt.

.. note::
    Inzwischen läuft auch das
    :doc:`RoboPlus-Tool </hardware/teile/motor/roboplus>` halbwegs vernünftig.



Starten
=======

Das Tool kann mit dem Befehl :program:`dxl_monitor` auf dem Darwin ausgeführt
werden. Falls dies nicht funktioniert, die Installation überprüfen.



Kommandos
=========

Man hat folgende Befehle zur Auswahl::

    exit                Exits the program
    scan                Outputs the current status of all Dynamixels
    id [ID]             Go to [ID]
    d                   Dumps the current control table of CM-730 and all
                        Dynamixels
    reset               Defaults the value of current Dynamixel
    reset all           Defaults the value of all Dynamixels
    wr [ADDR] [VALUE]   Writes value [VALUE] to address [ADDR] of current
                        Dynamixel
    on/off              Turns torque on/off of current Dynamixel
    on/off all          Turns torque on/off of all Dynamixels

Die wichtigen Kommandos hierbei sind::

    scan                zeigt Daten an
    id [VALUE]          zu einer ID wechseln
    wr 3 [VALUE]        ID des Dinges, auf dem man ist, wechseln (hier gehen
                        auch Nummer <255 die nicht belegt sind)
    wr 4 [VALUE]        Baudrate wechseln (hier machen meist nur 1 oder 34 Sinn)



.. _Motoren-ID setzen:

Motoren-ID setzen
=================

Ein typisches Verfahren ist also z.B. folgendes: Wir haben Motor 12 mit einem
brandneuen Motor gewechselt. Neue Motoren haben automatisch **ID 1** und
**Baudrate 34**. Alte Motoren behalten ihre ID und Baudrate 1, können aber auch
mal auf Baudrate 34 wechseln.

1. :command:`scan`: Wir sehen, dass ein FAIL bei 12 ist
2. :command:`wr 4 1`: Die Baudrate vom Board neu setzen
3. :command:`scan`: Wir sehen jetzt ein OK bei ID 1 und sonst ein FAIL, weil wir
   die Baudrate 34 betrachten
4. :command:`id 1`: Auf den Motor wechseln
5. :command:`wr 3 12`: Die ID auf 12 setzen
6. :command:`wr 4 1`: Die Baudrate auf 1 setzen
7. :command:`id 200`: Aufs Board wechseln
8. :command:`wr 4 1`: Die Baudrate vom Board neu setzen
9. :command:`scan`: Wir sehen jetzt hoffentlich nur TRUE

Bei einem FAIL kann es folgende drei Möglichkeiten geben:

1. Motor ist nicht angeschlossen (Kabel prüfen)
2. Baudrate ist auf 34 (:command:`wr 4 34` und :command:`scan`)
3. 2 Motoren haben gleiche ID und Baudrate

Bei Punkt 3 bietet sich folgende Strategie an: Alle Motoren abstecken, die man
nicht braucht. Das macht es manchmal einfacher, weil man nur einen Motor sieht,
wenn 2 die gleiche ID haben

Wenn alles gesetzt ist, muss **NICHT MEHR** die Firmware geupdaten werden, damit
die maximalen Winkel richtig gesetzt werden! Es kann einfach der Befehl
:command:`reset all` einmal im :program:`dxl_monitor` aufgerufen werden. Hierbei
werden die Motorwerte ihrer ID entsprechend gesetzt.



Installation
============

.. note::
    Folgende Installation ist nur nötig, wenn man das Programm nicht direkt mit
    :program:`dxl_monitor` aufrufen kann. Normalerweise sollte es schon auf den
    Darwins installiert sein.

Das Hersteller-Repository klonen::

    svn co https://bitbotsop.svn.sourceforge.net/svnroot/darwinop

Dann in den Unterordner *Linux/build* die Datei *LinuxCamera.cpp* öffnen und
folgende If-Blöcke auskommentieren::

    //    if (-1 == stat (devName, &st)) {
    //        fprintf (stderr, "Cannot identify '%s': %d, %s\n",
    //                 devName, errno, strerror (errno));
    //        exit (EXIT_FAILURE);
    //    }

    //    if (!S_ISCHR (st.st_mode)) {
    //        fprintf (stderr, "%s is no device\n", devName);
    //        exit (EXIT_FAILURE);
    //    }

Darauf folgend im Ordner *trunk/bitbots/Linux/project/dxl_monitor*
:command:`make` ausführen. Nun kann man die neue Datei mit
:command:`./dxl_monitor` ausführen.
