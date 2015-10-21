.. _pr-bitbotsSoftware:

Software Probleme auf dem Darwin
********************************

Häufige Fehler
==============

Class.name: Size missmatch:
---------------------------

Dieses Problem trit auf wenn eine Basisklasse verändert wurde und nciht alles
davon abhängende neu Compiliert wurde. Kann bei den folgenden Klassen
auftreten:

* IPC
* motionserver
* debug

Das einfachste ist den Buildordner zu löschen und damit ein Cleanbuild zu
machen::

    rm -rf .build/*



System neu installieren:
------------------------

$ wget http://olli.keller-delirium.de/system.raw.bz2

System auf den Stick /dev/sdX installieren
$ bzip2 -d < system.raw.bz2 | dd of=/dev/sdX bs=4M


WLAN einrichten:
----------------

Das W-LAN wird unter */etc/NetworkManager/system-connections/* Konfiguriert.
Für jedes Netz gibt es dort eine Datei mit dem namen des APs
(Der Networkmanager sorgt dafür das die Dateien richtig heißen). Die Datei für unser
Netzwerk sieht folgendermaßen aus::

    [connection]
    id=BitBots
    uuid=a40078ea-6efc-414c-8aa6-02361bd2b51b
    type=802-11-wireless

    [802-11-wireless]
    ssid=BitBots
    mode=infrastructure
    security=802-11-wireless-security

    [802-11-wireless-security]
    key-mgmt=wpa-psk
    auth-alg=open
    psk=unsereUltrageheimePassphrase

    [ipv4]
    method=auto

    [ipv6]
    method=auto
    ip6-privacy=2

Sonstige Softwareprobleme
=========================

debug-ui-neu startet nicht
--------------------------

Wenn Die debugui mit der Fehlermeldung das pygobject feht nicht startet
versuche volgendes::

    pip uninstall pygobject
    sudo aptitude install python-gobject

eventuell wird noch das -dev packet benötigt.
