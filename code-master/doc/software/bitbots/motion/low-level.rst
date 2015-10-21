
Low-Level Kommunikation
=======================

Im Gegensatz zum `NAO <http://www.aldebaran-robotics.com/>`_ ist die Hardware
und der Zugriff auf diese auf dem Darwin frei.
Der Darwin besitzt ein kleines Board `CM 730`_ in der Brust, welches
neben der Kontrolle der LEDs auch die Sensoren besitzt.
Das Board ist an einen seriellen Datenbus angehängt, an dem auch die Gelenke
angeschlossen sind. Es handelt sich um `MX 28`_ Aktuatoren.
Wir können direkt Anfragen auf diesen Bus schreiben und die Antworten
auslesen.

Sowohl der `MX 28`_ als auch der `CM 730`_ besitzen eine kleine Datentabelle
mit ihrer aktuellen Konfiguration. Dort stehen z.B. die aktuellen Gelenkwinkel
drinne. Einige Felder lassen sich nicht nur auslesen, sondern auch
beschreiben, um den Zustand der Hardware zu verändert.

Die Kommunikation erfolgt über ein einfaches `Protokoll`_, in dem
Anfragen immer vom Computer ausgehen und stets durch Antwortpakete
beantwortet werden. Es gibt Pakete zum Auslesen von Werten aus den
Datentabellen und zum Schreiben in diese. Ein Paket wird immer direkt
an ein Zielkontroller gesendet.



CM 730
------

Das `CM 730`_ Board sitzt in der Mitte des Torsos.
Auf dem Board ist der Beschleunigungs- und Winkelbeschleunigungssensor
verbaut. Es wird über die Adresse 200 angesprochen.

Die wichtigsten Felder aus der Registertabelle des `CM 730`_ sind

.. describe:: dxl_power

    Ein Byte an der Stelle 24 in der Tabelle. Wird es auf eins gesetzt, so
    werden alle Gelenke aktiviert. Es können nur Schreib- und Leseanfragen an
    aktive Gelenke gesendet werden. Schreibt man Null in dieses Register,
    gehen die Gelenke aus und der Roboter bricht zusammen.


.. _led_head:
.. describe:: led_head

    An der Stelle 26 in der Registertabelle steht hier die Farbe der
    LED oben zwischen den Augen. Die Farbe wird mit zwei Byte kodiert, wobei
    jedem Farbwert fünf Bit zugesprochen wird.
    ::

        # Kodieren
        word = ((b>>3) << 10) | ((g>>3)<<5) | (r>>3)

        # Dekodieren
        r = (word & 0x1f) << 3
        g = ((word >> 5) & 0x1f) << 3
        b = ((word >> 10) & 0x1f) << 3


.. describe:: eye_head

    Farbwert an der Stelle 28. Dies ist die aktuelle Farbe der Augen,
    siehe auche `led_head`_.


.. _gyro:
.. describe:: gyro

    Ab Byte 38 stehen hier in drei 16bit-``short``-Werten die Werte des
    Winkelbeschleunigungssensors drinne. Die Werte liegen pro Komponente
    zwischen 0 und 1023. Im Ruhezustand sollte der Wert genau 512 betragen.


.. describe:: accel

    Ab Byte 44 stehen hier die Komponenten des Beschleunigungsvektors drinne.
    Diese sind kodiert wie `gyro`_.



MX 28
-----

Es sind als Gelenke die Aktuatoren `MX 28`_ verbaut.

.. todo::
    Wichtigsten Felder aus der Registertabelle aufschreiben.

Protokoll
---------

Bei dem Protokoll, dass für die Kommunikation mit der Hardware verwendet wird,
handelt es sich um ein einfaches synchrones Protokoll. Das Programm,
im folgenden *Client* genannt, stellt Anfragen an die Hardware, die dann
stehts mit einem :class:`controller.StatusPacket` antwortet. In diesem
sind dann die eventuell angeforderten Daten. Es ist möglich, die Hardware
anzuweisen, diese Pakete nicht zu senden, darauf wird hier jedoch
nicht eingegangen.

Anfrage
+++++++

Jedes Paket beginnt mit zwei ``0xff`` Bytes. Befindet man sich in einem
*kaputten* Datenstrom, so muss man einfach solange lesen, bis man auf
zwei ``0xff`` Bytes stößt. Kann man dort beginnend ein Paket parsen,
so hat man wieder einen Einstieg gefunden.

Im dritten Byte ist die
Zieladresse des Hardware-Kontrollers gespeichert, der angesprochen
werden soll. Dem `CM 730`_ ist die Adresse 200 zugeordnet. Die Gelenke haben
die Adressen 1 bis 21. Es gibt eine Broadcast-Adresse (254), auf die alle an
den Bus angeschlossenen Kontroller antworten. Dies ist nützlich, um die
komplette Hardware gleichzeitig zu aktivieren.

Das vierte Byte beschreibt die Länge des Datenpakets. Es werden die
Anzahl der Bytes des Pakets minus vier gespeichert. Dies entspricht
der Anzahl der Bytes, die in diesem Paket noch folgen. Ist ein Paket also
insgesammt (von ``0xff`` bis zur Prüfsumme) sechs Byte lang, wird hier
die Länge zwei gespeichert.

Im fünften Byte wird die Art der Anfrage beschrieben.
Es wird zwischen acht unterschiedlichen Anfragetypen unterschieden.

=========== ==========  =======================================================
Wert        Name        Beschreibung
=========== ==========  =======================================================
``0x01``    Ping        Dieser Pakettyp kann genutzt werden, um zu
                        bestimmen, ob die adressierte Hardware aktiv ist und
                        auf Anfragen reagiert. Es wird nichts an der Hardware
                        verändert.
``0x02``    Read        Mit diesem Pakettyp kann man ab einer bestimmten
                        Stelle ein oder mehrere Werte hintereinander aus der
                        Hardware auslesen.
``0x03``    Write       Schreiben von einem oder mehreren
                        aufeinanderfolgenden Werten in die Hardware.
``0x04``    RegWrite    Dieser Pakettyp ist ähnlich wie ein
                        normales *Write*-Paket. Die Änderungen werden jedoch
                        nicht sofort wirksam, sondern erst durch ein
                        *Action*-Paket angewand.
``0x05``    Action      Siehe oben.
``0x06``    Reset
``0x83``    SyncWrite   Mit einem *SyncWrite*-Paket können
                        mehrere Kontroller gleichzeitig beschrieben werden.
``0x92``    BulkRead    Mit einem *BulkRead*-Paket können Werte
                        aus mehreren Kontrollern gleichzeitig gelesen werden.
=========== ==========  =======================================================

Abhängig von dem Pakettyp folgen dann die Parameter bzw. Daten.
Diese werden in der Dokumentation der einzelnen Datenpakete genauer
beschrieben.

.. _checksum:

Am Ende jeden Pakets steht eine Prüfsumme. Die Prüfsumme berechnet sich
dabei als das Einerkomplement der Summe aller Bytes (natürlich ohne
die Prüfsumme). In Python-Code berechnet sich die Prüfsumme als::

    def checksum(packet):
        return ~sum(packet[:-1]) & 0xff

Antwort
+++++++

Die Antwort auf eine Anfrage ist ähnlich formatiert. Jedes Antwortpaket
beginnt mit zwei ``0xff`` Bytes gefolgt von der ID des Absenders.
Diese ist besonders nützlich bei Broadcast-Anfragen oder BulkRead-Paketen.
Im vierten Byte ist wieder die Anzahl der noch folgenden Bytes gespeichert.

Statt der Anfragetyp wird an der fünften Stelle im Antwortpaket der
(Fehler-)Status gespeichert. Hat dieses Byte den Wert Null, so ist die
Anfrage erfolgreich ausgeführt worden. Ist ein Fehler aufgetreten,
so wird dieser durch ein oder mehrere gesetzte Bits im Byte beschrieben.

=============== ==========================================================
Bit gesetzt     Name
=============== ==========================================================
7               Nicht verwendet
6               Undefinierte/Fehlerhafte Instruktion
5               Zu viel Last auf diesem Motor
4               Prüfsumme des Pakets ist fehlerhaft
3               Ein Wert ist außerhalb des gültigen Bereichs
2               Der Motor ist überhitzt
1               Die Zielposition ist außerhalb des gültigen Bereichs
0               Die angelegte Spannung ist zu hoch.
=============== ==========================================================

Nach dem Statusbyte folgen die eventuell angeforderten Daten. Die
Antwort wird durch eine :ref:`Prüfsumme <checksum>` abgeschlossen.

Implementation
--------------

.. automodule:: bitbots.lowlevel
