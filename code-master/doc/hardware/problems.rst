Hardware Troubleshooting
************************



Kamera
======

.. todo:: Es fehlt eine nähere Beschreibung von der Kamera



Kamera nicht gefunden
---------------------

* In den USB-Devices nachschauen, ob sie dort gefunden wird. Hierzu einfach
  :command:`lsusb` eingeben. Falls der Befehl nicht funktioniert muss das Paket
  :program:`usbutils` installiert werden.
* Ersatzkamera anschließen und noch einmal versuchen
* Release Version unserer Software als Test darauf flashen.
* Kabel mit Multimeter durchtesten



Motorprobleme
=============



Motor nicht gefunden
--------------------

.. ditaa::
    +---------------------------------------------------+
    | Kabelverbindungen zwischen dem fehlenden Motor    |
    | und dem nächsten gefundenen prüfen (wiring_manual)|
    +-+-------------------------------------------------+
      | Misserfolg
      v
    +-+------------+ Motor manchmal  +----------------+         +------------------------+
    | dxl_monitor  | gefunden        | killall screen | Erfolg  | Mehrere Programme  {d} |
    | n mal 'scan' +---------------->| killall python +-------->| haben vmtl. zeitgleich |
    +-+---------+--+                 +---------+------+         | die Hardware benutzt   |
      |         | Motor nie                    | Misserfolg     +--------------------+---+
      |         | gefunden  +-----------+      v                                     ^
      |         +---------->+ Alle      | +----+---+ Erfolg  +----------------+ oder |
      |                     | anderen   | | Reboot +-------->| Softwarefehler +------+
      | Motor immmer        | Motoren   | +----+---+         +----------------+
      | gefunden            | entfernen |      |              +---------------------+
      v                     +----+------+      | Misserfolg   | Mit Roboplus oder   |
    +-+---------------+          |             +------------->+ Servotool testen{io}|
    | Besteht Problem |          v                            +-------------------+-+
    | überhaupt noch? |     +----+----+ Kein Motor gefunden                       ^
    +-+---------------+     | scannen +-----------------+                         |
      | Ja                  +----+----+                 |                         |
      v                          |                      v                         |
    +------------------------+   | Motor gefunden      ++------------------+      |
    | Blindtest der Software |   | mit falscher ID     | Auf Baudrate 34   +------+
    | auf funktionierender   |   v                     + (default) scannen | Misserfolg
    | Hardware               | +-+-------------------+ +----+--------------+
    +---+--------------------+ | Motor hat falsche{d}|      | Erfolg
        |                      | ID. Mit dxl_monitor |      |
        | Fehler               | korrekte ID setzen  |      V
        v                      +---------------------+ +-+-----------------+
    +---------------------------+                      | Motor hat falsche |
    | Zurücksetzen der Software |                      | Baudrate. Mit     |
    | auf vorige Version        |                      | dxl_monitor   {d} |
    +---+-------------------+---+                      | korrigieren       |
        |                   |     Problem schwindet    +-------------------+
        | Problem besteht   +----------+
        v                              |
    +---+--------------------------+   v
    | Die Software beschädigt {d}  | +-+---------------------+
    | unsere Hardware. Z.B. durch  | | 0/8/15 Softwarefehler |
    | zu schnelles Stromabschalten | | ggf. Master reverten  |
    | nach einem Schreibzugriff.   | | und in neuem Branch   |
    | Schlage ALARM!!!             | | fixen.                |
    +------------------------------+ +-----------------------+

Es gibt mehrere Möglichkeiten, warum unsere Motion einen Fehler wirft, weil sie
einen oder mehrere Motoren nicht findet.



.. _Motorfehler Punkt 1:

1.  | Sicherstellen, dass es ein Hardwareproblem ist
    |     :program:`dxl_monitor` aufrufen und mehrfach :command:`scan` drücken
    |         Motor wird immer gefunden -> :ref:`Punkt 4 <Motorfehler Punkt 4>`
    |         Motor wird manchmal gefunden ->
              :ref:`Punkt 3 <Motorfehler Punkt 3>`
    |         Motor wird niemals gefunden ->
              :ref:`Punkt 5 <Motorfehler Punkt 5>`



.. _Motorfehler Punkt 2:

2.  | Es handelt sich vielleicht um ein Softwareproblem
    |     Identische Software auf einem anderen Roboter ausführen
    |         Gleiche Fehler -> Es ist ein Softwareproblem
    |         Funktioniert -> :ref:`Punkt 12 <Motorfehler Punkt 12>`



.. _Motorfehler Punkt 3:

3.  | Wahrscheinlich schickt irgendeine Software Pakete an die Motoren, was zu
      Störungen führt.
    |     :command:`killall screen` und :command:`killall phyton` aufrufen und
          nochmal testen
    |         Ergebnis hat sich geändert -> :ref:`Punkt 1 <Motorfehler Punkt 1>`
    |         Ergebnis hat sich nicht geändert ->
              :ref:`Punkt 4 <Motorfehler Punkt 4>`



.. _Motorfehler Punkt 4:

4.  | Sichergehen, dass es kein Problem mit dem :program:`dxl_monitor` gibt
    |     Versuchen den Motor mit :program:`Roboplus` oder dem Darmstädter Tool
          zu finden
    |         Motor wird immer gefunden -> :ref:`Punkt 2 <Motorfehler Punkt 2>`
    |         Motor wird manchmal gefunden ->
              :ref:`Punkt 13 <Motorfehler Punkt 13>`
    |         Motor wird niemals gefunden ->
              :ref:`Punkt 5 <Motorfehler Punkt 5>`



.. _Motorfehler Punkt 5:

5.  | Sicherstellen, dass nicht 2 Motoren die gleiche ID haben
    |     Nur einen Motor, der nicht gefunden wird, anschließen und scannen
    |         Motor wird gefunden -> :ref:`Punkt 6 <Motorfehler Punkt 6>`
    |         Motor wird nicht gefunden -> :ref:`Punkt 7 <Motorfehler Punkt 7>`



.. _Motorfehler Punkt 6:

6.  | Es gibt Motoren mit gleicher ID
    |     Den Motoren die richtigen IDs geben
          (:ref:`siehe Doku <Motoren-ID setzen>`)
          und dann alle Motoren anschließen und scannen
    |         Alle Motoren gefunden -> Software nochmal laufen lassen
    |         Weiterhin fehlerhafte Motoren ->
              :ref:`Punkt 1 <Motorfehler Punkt 1>`



.. _Motorfehler Punkt 7:

7.  | Sicherstellen, dass der Motor nicht auf seiner Standard-Baudrate ist
    |     Auf Baudrate 34 scannen
          (:ref:`siehe Doku <Benutzung des ServoTools>`)
    |         Motor wird gefunden -> Baudrate auf 1 setzen
              (:ref:`siehe Doku <Benutzung des ServoTools>`)
    |         Motor wird nicht gefunden -> :ref:`Punkt 8 <Motorfehler Punkt 8>`



.. _Motorfehler Punkt 8:

8.  | Sicherstellen, dass es kein Problem mit dem Kabel gibt
    |     Kabel durch ein anderes ersetzen und nochmal scannen
    |         Motor wird gefunden -> Fehlerhaftes Kabel wegschmeißen oder als
              fehlerhaft kennzeichnen und mit neuem Kabel weiterarbeiten
    |         Motor wird nicht gefunden -> :ref:`Punkt 9 <Motorfehler Punkt 9>`



.. _Motorfehler Punkt 9:

9.  | Sicherstellen, dass man keinen grundlegenden Fehler gemacht hat
    |     Reservemotor, von dem man weiß, dass er funktioniert, an die
          entsprechende Stelle anschließen und scannen
    |         Reservemotor wird gefunden (auch unter einer falschen ID) ->
              :ref:`Punkt 10 <Motorfehler Punkt 10>`
    |         Reservemotor wird nicht gefunden -> Wir haben etwas grundsätzlich
              falsch gemacht. Nochmal genau nachdenken und sonst jmd. anderes um
              Hilfe fragen.



.. _Motorfehler Punkt 10:

.. todo:: Verlinkung zur Doku

10. | Firmwarewiederherstellung versuchen
    |    Mit Hilfe von :program:`RoboPlus` eine Firmwarewiederherstellung machen
         (:ref:`siehe Doku <Motor-Firmware updaten>`)
    |        Der Motor wird erfolgreich wiederhergestellt -> Motor ist nun auf
             ID 1, Baudrate 34 und muss nur umgesetzt werden (siehe Doku)
    |        Der Motor kann auch dort nicht gefunden werden ->
             :ref:`Punkt 11 <Motorfehler Punkt 11>`



.. _Motorfehler Punkt 11:

11. | Auf allen Baudraten nach dem Motor suchen
    |     Mit :program:`Roboplus` eine vollständige Suche durchführen
          (:ref:`siehe Doku <RoboPlus Fehlerbehandlung>`)
    |         Motor wird gefunden -> Baudrate wieder auf 1 setzen
    |         Motor wird nicht gefunden -> eine andere Person um Hilfe bitten



.. _Motorfehler Punkt 12:

12. | Motor wird von Tools gefunden, Software wirft trotzdem Fehler
    |     Andere Person um Hilfe bitten



.. _Motorfehler Punkt 13:

13. | Motor wird manchmal gefunden und manchmal nicht
    |     Meistens irgendein Problem von Paketen, die gesendet werden. Roboter
          nochmal neu flashen und neustarten und alles killen, was etwas an die
          Motoren senden könnte.
    |     Wackelkontakte am Kabel könnten natürlich auch möglich sein.



Stromversorgung
===============

Ziehe bei solchen Problemen wenn möglich den zuständigen Hardware-Supervisor
hinzu.

.. ditaa::
    +----------------+      +---------------+      /--------\
    | Fehler im      | Nein + Fehler im     | Nein | Hau ab,|
    | Netzbetrieb?   +----->+ Akkubetrieb?  +----->+ Idiot  |
    +-------+--------+      +-------+-------+      \--------/
            | Ja                    | Ja
            v                       v
    +-------+---------+  +----------+---+ Problem schwindet +------+
    | Fehler im       |  | Tausche Akku.+------------------>+ {io} |
    | Akkubetrieb?    |  +------+-------+                   | Akku |
    +-+------------+--+         | Problem                   +------+
      | Nein       | Ja         v besteht
      v            |     +------+----------+ Problem schwindet  +---------+
    +-+----------+ |     | Tausche Adapter +------------------->+ {io}    |
    | Darwin {io}| |     +------+----------+                    | Adapter |
    | Netzstecker| |            | Problem                       +---------+
    +------------+ |            v besteht
                   |     +------+-----+
                   +---->+{io}        |
                         | Powerboard |
                         +------------+



Adapter
-------

.. glossary::

    Männlicher Tamya-Stecker hat einen Wackelkontakt
        Ähnliches Problem wie beim Akku, nur auf der Adapter-Seite

    Defekte Lötstelle am T-Stecker
        Die Lötstellen am T-Stecker sind gut eingepackt mit Vulkanisierband und
        Schrumpfschlauch, da der Darwin auf diese Stelle drauffallen kann. Da
        die Isolierung zur endgültigen Diagnose entfernt werden muss, sollten
        vorher die anderen Ursachen ausgeschlossen sein. Reißen beide Lötstellen
        gleichzeitig und vollständig ab, könnte es zu einem Kurzschluss kommen.
        Das ist jedoch sehr unwahrscheinlich.

    Kabelbruch
        Wir benutzen feinadrige Litzen mit Silikon-Mantel. Die sind kaum
        anfällig gegen Kabelbruch, außer an den Enden, wo sie fixiert sind.



Akku
----

.. warning::
    Fehlerhafte Akkukontakte sind sehr gefährlich. Kommt es zum Kurzschluss
    wird der Akku beschädigt und kann schlimmstenfalls explodieren. Beschädigte
    Akkus müssen sofort aus dem Verkehr gezogen, elektrisch isoliert,
    **eindeutig** markiert und bis zur Reparatur sicher aufbewahrt werden.

.. glossary::

    Tamya-Stecker hat einen Wackelkontakt
        Tamya-Stecker sind störanfällig. Im Steckergehäuse befinden sich zwei
        vergoldete Kontakte, welche mit dem Kabel vercrimpt sind. Die Kontakte
        sind über Wiederhaken mit dem Steckergehäuse verbunden. Verbiegen die
        Wiederhaken durch ruppige Benutzer, können die Kontakte nach hinten aus
        dem Stecker rutschen.

        Sofern die Wiederhaken noch intakt sind, kann man sie wieder aufbiegen
        und die Kontakte neu im Gehäuse verankern. Ansonsten muss der Stecker
        getauscht werden.

    Kabel aus dem Crimp gerissen
        Bei fehlerhaften Crimpverbindungen, insbesondere in Verbindung mit
        unsachgemäßem Ziehen am Kabel, können Stromkabel aus dem Stecker reißen.
        Hier hilft nur noch ein Neuvercrimpen des Steckers.



Netzstecker
-----------

.. glossary::

    Netzteilstecker sitzt nicht richtig
        Unsere Stecker sind nicht passgenau. Das Problem lässt sich abmildern,
        indem man mit einem kleinen Schlitzschraubendreher den Metallstift im
        weiblichen Stecker des Darwins vorsichtig ein wenig aufbiegt (ohne ihn
        abzubrechen).



Powerboard
----------

.. ditaa::
    +---------------+
    | Fehler nur im | Nein       +--------+
    | Akkubetrieb   +----------->+ Platine|
    +--+------------+            +-----+--+
       | Ja                            ^
       v                               |
    +-----------+ falls Problem besteht|
    | T-Stecker +----------------------+
    +-----------+



T-Stecker
'''''''''

Am Stecker sind zwei Metallklammern. Diese können durch Abnutzung
zusammengedrückt werden, sodass sie keinen zuverlässigen Kontakt mehr herstellen
können. Am besten man legt einen kleinen Imbus unter die Metallbügel und biegt
mit einer Zange die Klammer so um den Imbus, dass die notwendige Wölbung
wiederhergestellt wird.



Platine
'''''''

Bisher sind keine nennenswerten Probleme aufgetreten.
