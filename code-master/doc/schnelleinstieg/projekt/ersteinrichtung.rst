.. _software_einrichten:

Erstmaliges Einrichten des Projekts
===================================

Die Einrichtung des Projekts dauert eine Weile. 
Bitte kümmere dich rechtzeitig darum das Projekt aufzusetzen.

.. hint:: 

  Die folgende Beschreibung ist für nutzer eines Debian-Basierten Systems (z.B. Ubuntu) gedacht.
  Wer eine andere \*nix-Distribution benutzt wird höchstwahrscheinlich wissen was er tut und kann die 
  her gegebene Anleitung entsprechend übertragen.

  Wer Windows, oder Mac benutzt, hat ein grundsätzliches Problem dem können wir ohnehin nicht helfen.

0. Schritt - Voraussetzungen
----------------------------
Folgendes sollte für dich gelten:

* Linux-System
* Account im :ref:`sec_redmine` für uns freigeschaltet.
* Public-Key im Redmine eingetragen
* Du hast rudimentär Ahnung was :ref:`git` ist.

.. _git-einrichten:

1. Schritt - Git 
----------------

Ein eingetragener Key im Redmine ermöglicht es dir folgenden Befehl auszuführen ::

  git clone gitolite@git.mafiasi.de:robocup/code [ordnername]

dies erstellt einen unterordner im aktuellen Verzeichnis in den unser gesamter Quellcode zusammen mit allen jemals existierenden Versionen kopiert wird. Das dauert also eine Weile.
In der zwischenzeit kannst du schon mal weitere Doku lesen.

.. hint::

  Wenn du *ordnername* nicht angegeben hast, wird "code" als name benutzt.

2. Schritt - Abhängigkeiten
---------------------------

Wechsel nun in das erstelle Verzeichnis.
In einer Idealen Welt genügt nun der folgende Befehl einzugeben um die 
Abhängigkeiten zu installieren ::

  infrastruktur/setup/install.sh

Das Script wird nach deinem Root-Passwort fragen um die Systemweiten
Abhängigkeiten installieren zu können.

Achte bitte in der Ausgabe des Scriptes auf Probleme und versuche diese ggf. zu beheben.
Im Zweifelsfall such dir hilfe bei einem anderen AG-Mitglied.

Um die debug-ui benutzen zu können musst du noch zusätzlich folgenden befehlt ausführen(im virtualenv!)::

  pip install pygtk

Dieser Installationsbefehl liegt absichtlich nicht im install-skript, weil das nicht auf dem Roboter landen soll (da es etwas grafisches ist).
  

.. hint::
  Die Abhängigkeiten werden nicht benötigt, wenn du ausschließlich im :ref:`chroot` arbeiten möchtest, da die abhängigkeiten im chroot bereits erfüllt werden.
  
Folgen
------

Du hast nun lesenden und Schreibenden zugriff auf unseren Quellcode.
Auf deinem Rechner ist ein :ref:`virtual-env` eingerichtet, 
Welches es dir ermöglicht in einen speziellen Modus zu wechseln 
in dem unsere Software lauffähig ist.


Optionales
----------

Falls man viel Programmieren möchte sollte man sich eine IDE einrichten. Für Pyhton bietet sich dort pycharm an,
was auch von vielen AG-Mitgliedern benutzt wird.

Installation
^^^^^^^^^^^^

Community Version hier runter laden und installieren::

    http://www.jetbrains.com/pycharm/download/

Um dann das Projekt einzurichten klickt man auf +#TODO sowas wie open existing folder+ und wählt den git Ordner
(code) aus

Nun sollte man links in pyhcarm den Dateibaum des gits sehen.

Um den richtigen Wurzelpunkt für unsere Imports festzulegen klicken wir den Ordner lib mit rechts an und klicken dann
auf "Mark directory as -> Source root".

.. todo::
    richtige Python version einstellen

