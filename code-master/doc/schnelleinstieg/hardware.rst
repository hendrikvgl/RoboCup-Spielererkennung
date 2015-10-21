.. _hardware schnelleinstieg:

Hardware Schnelleinstieg
************************

Am besten kommt man mit der Hardware in Kontakt wenn man als "Azubi" 
mit jemand anderem zusammen an den Robotern herum schraubt.
Auf dieser Seite findest du ein paar wichtige Hinweise darüber wie 
wir mit der Hardware arbeiten.

Ausführlichere Detaildoku existiert in der Rubrik :ref:`sec_hardware` 


Inventarnummern
===============

.. warning:: 
  Deprecated seit Oktober 2014
  wir haben jetzt ein neues Inventarsystem mit Datenbank und Barcode-Scanner.

  .. todo::
    **Hardware - Inventar**

    Neues Inventarsystem dokumentieren


Jedes Teil, über dessen Verbleib, Zustand oder Werdegang wir informiert sein
möchten, sollte eine Inventarnummer bekommen.

Inventarnummern starten bei *000* und enden bei *ZZZ*. Der Buchstabe "O" wird
wegen der Verwechslungsgefahr mit der Null nicht vergeben. Ähnliche Probleme
könnte es mit "1" vs. "l" etc. geben. Da bitte umsichtig sein. *009* liest
sich auf dem Kopf wie *600* usw.

Eine Besonderheit sind die Motornummern. Die sind nur zweistellig und bestehen
jeweils aus einem Buchstaben und einer Ziffer, also *A0* bis *Z9* (Verfahren
historisch gewachsen).

Teile mit Inventarnummer bekommen einen Eintrag in der Inventardatenbank.

.. todo:: Link auf zu schreibende Inventardatenbanksdoku.



Schrauben
=========

* Lose Schrauben nicht herumfliegen lassen, gleich in eine Schachtel,
  ggf. beschriften
* Schrauben, die länger gelagert werden, kommen wieder in den Schraubenkasten
* In der Assembly-Manual prüfen, welche Schraube verwendet werden muss.
  **Nicht ausprobieren!**
* Schrauben, die sich regelmäßig lösen, oder in die Elektronik fallen könnten,
  mit Schraubenfixierer **sparsam** behandeln.
* Nach fest kommt lose; Schrauben nicht zu fest anziehen, das beschädigt
  die Gewinde, die Schraubenköpfe und das Werkzeug und bereitet Probleme
  beim Wiederausbau. Falls die Schraube sich löst -> Schraubenfixierer.
* Auf einer vernünftigen Unterlage arbeiten; es fallen dann weniger Schrauben
  herunter und wenn, dann teleportieren sie sich nicht gleich in eine andere
  Dimension.



Sortierkästen
=============

In den Laborschubladen sind überall Sortierfächer. Diese zweckentfremden wir,
um Teile übersichtlich zu lagern. Jeder Roboter sollte sein eigenes Sortierfach
haben, damit dort ihm zugehörige Teile abgelegt werden können.



Elektronik
==========

* Keine Kleinteile auf die Platine fallen lassen
* Vorm Einschalten den Darwin kippen, um zu hören, ob irgendwo eine Schraube
  herumkullert
* Immer Erden vor dem Anfassen von Platinen!
* Elektronikarbeiten auf der angeschlossenen Antistatikmatte durchführen
* Gelagerte Platinen mit Antistatikfolie gegen Entladungen schützen
* Beim Durchmessen von Teilen überlegen, was man tut. Für viele Messungen
  legt das Gerät selbst eine Spannung an, außerdem kann man mit dem Messgerät
  Kurzschlüsse erzeugen!
* Im Zweifelsfalle einen Fachmann zu Rate ziehen



Roboterübersicht
================

Es gibt für die einzelnen Roboter Übersichtsseiten im Redmine-Wiki. Wenn
Veränderungen an der Hardware festgestellt oder vorgenommen werden, muss die
jeweilige Seite aktualisiert werden. Die Seiten sind:

* Gesamtübersicht_
* Glados_
* Wheatly_
* Atlas_
* Tamara_
* Wilma_



Hardware Doku
=============

Es gibt einen Ordner "Hardware Doku" mit allen Schaltplänen, Bauplänen,
Risszeichnungen etc. Wenn neue Dokumente benötigt werden, bitte ausdrucken und
dort hinzufügen. Eine digitale Kopie gehört in das Verzeichnis
"technischeDokumente" im Orga-Git. Nach eigenem Ermessen sollten weitere Kopien
kritischer Dokuabschnitte überall dort hin geklebt werden, wo sie oft gebraucht
werden. Wo immer du die Arbeit erleichtern kannst, tu es.



Besonders wichtige Dokumente
----------------------------

.. glossary::

    Assembly-Manual
        Welches Teil sitzt wo und ist mit welcher Schraube wie befestigt.
        Übersicht über alle Bauteile mit Nummer. Schematische Ansichten.

    Wiring-Manual
        Ähnlich der Assembly-Manual, nur mit Kabeln. Also eine Übersicht über
        alle Kabel und wo sie sitzen und wie sie befestigt werden. Sowohl
        schematische Zeichnungen als auch Fotos.



Robotis Tutorials
=================

Robotis hat auf ihrem YouTube-Kanal einige Videos_ hochgeladen, die bei einigen
häufigen Reparaturen und Problemen helfen sollen.


Inventor
========

Audodesk Inventor ist ein 3D CAD Programm, womit wir unsere neuen Roboter konstruieren.

.. hint::
    Marc 0bestman hat ein AG-internes Video_ gedreht, in dem er Inventor erklärt.


Es gibt im Internet sehr viel Dokumentation zu Inventor, weil es in der Industrie viel benutzt wird, aber auch wir haben hier eine kleine Doku angelegt.


Schnelleinstieg nicht ausführlich genug? 
Lies weiter in der Sektion :ref:`sec_hardware` :)

.. _Gesamtübersicht: http://redmine.mafiasi.de/projects/robocup/wiki/Hardwarestatus
.. _Glados: http://redmine.mafiasi.de/projects/robocup/wiki/Glados
.. _Wheatly: http://redmine.mafiasi.de/projects/robocup/wiki/Wheatly
.. _Atlas: http://redmine.mafiasi.de/projects/robocup/wiki/Atlas
.. _Tamara: http://redmine.mafiasi.de/projects/robocup/wiki/Tamara
.. _Wilma: http://redmine.mafiasi.de/projects/robocup/wiki/Wilma
.. _Videos: http://www.youtube.com/playlist?list=PLvaBFX_ny57TI62a7baE7tawH7opKDu99
.. _Video: http://data.bit-bots.de/Schulungsvideos/Inventor-Schulung.mp4
