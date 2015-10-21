Coding-Standards
****************

.. sectionauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

Dieses Dokument soll einen Überblick über unsere Codingstandards liefern.



Allgemeines
===========



Dateiheader
-----------

Dateiheader sollten sich immer an dem folgenden Schema orientieren::

    """
    ModulName
    ^^^^^^^^^

    Kurze Beschreibung wofür dieses Modul da ist.

    History:
    ''''''''

    * 1.4.12: Created (Nils Rokita)

    * 9.1.14: Wichtige Erweiterung: Nun mit Funktion1 und Eigenschaft5 (Max Musterman)

    * 9.1.14: Umstellung auf Eevents (Has Wurst)

    """

In C sind die ``"""`` durch Blockkommentar ``/* ... */`` zu ersetzen, Außerdem
ist es in C++ eventuell sinnvoll, nur die ``.hpp``-Datei zu kommentieren und in
der ``.cpp``-Datei nur kurz anzumerken, wo sie dazugehört.



Python
======

.. important::
    Im allgemeinen versuchen wir uns an den PEP8 Standart zu halten. Viele Entwicklungsumgebungen, wie z.B.
    pycharm überprüfen auch on-the-fly, ob man sich an diesen Standart hält.

Klassen
-------

Im Klassenkommentar sollte immer kurz der Zweck erläutert werden. Wenn das
schon im Modulkommentar passiert, ist ein Verweis darauf sinnvoll::

    """
    See :mod:name.des.modules
    """



Methoden
--------

Methodenkommentare sollten immer enthalten, wofür sie gedacht sind und was
sie machen.

Generell sollten alle Parameter mit Zweck und Datentyp dokumentiert werden.
Außerdem sollte der Rückgabetyp dokumentiert werden. Exceptions können mit
``:raises:`` dokumentiert werden::

    def test(self, text, zeit):
        """
        Diese Funktion testet das Zeitverhalten von ``text`` unter ``zeit``

        :param text: Der zu testene Text
        :type text: String
        :param zeit: Die zu testende Zeit in Sekunden
        :type zeit: int

        :return: Der Zeitverhaltensindexwert
        :rtype: int

        :raises ValueError: Wenn Zeit < 0
        :raises textError: Wenn der Text doof ist
        """

Wenn der Autor einer Funktion vom Modul/Klasse abweicht, kann der Autor auch
hier mit ``.. codeauthor::`` Dokumentiert werden



Namensgebung
------------

* Module werden kleingeschrieben
* Klassen in CamelCase
* Funktionen und Variablen in klein_mit_unterstrich
* Konstanten IN_CAPS
* Interne Methoden sollten mit ``_`` beginnen
* Bei Klassen, welche zum Überladen gedacht sind, und Gefahr für
	Namenkollisionen gibt können 2 Unterstriche vorangestellt werden.
   	Solche Methoden/Variablen werden von Python intern anders genannt.



Sonstiges
---------

Wir versuchen uns möglichst an den pep8-Codingstandard zu halten.

Das bedeutet über das oben genannte hinaus im Wesentlichen:

* Keine Zeile ist länger als 80 Zeichen
* Vor und nach Operatoren gehören in der Regel Leerzeichen
    (Ausnahme: Defaultparameter bei Funktionen)
* Einrückungen immer um 4 Lehrzeichen



Cython
======

Hier gelten überwiegend die Regeln wie für Python.

Importierte C / C++ Module sollten immer mit ``_Module`` benannt werden.
Es ist insbesondere darauf zu achten, dass die Modulenamen und Dateinamen
durchgehend kleingeschrieben werden, um unnötige Importfehler zu vermeiden.



C++
===

Interne Modulvariablen werden der Übersicht halber mit ``m_`` geprefixt.

Doku für C sollte immer kurz und knapp im Quelltext stehen. Ausführlichere
Funktionsdoku muss in eigenen Dokudateien im Dokuverzeichnis liegen, da
C / C++ Code nicht mit Autodoc erfasst werden können.

Bei längeren Blöcken (ID/while/for) sollte an der schließenden Klammer
das öffnende ``if`` als Kommentar stehen.
