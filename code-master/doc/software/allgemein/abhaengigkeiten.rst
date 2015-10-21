Abhängigkeiten des Programmcodes
================================

Hier die wichtigsten verwendeten Techniken und Biblioteken.

.. hint::
  Die diversen Python-Bibliotheken lassen sich speziell für unser :ref:`virtual-env` installieren,
  und sind dann nur bei *aktiviertem* Projekt verfügbar.
  Sie sind hier **nicht** aufgeführt, in dieser Sektion finden sich nur Bibliotheken die Systemweit 
  installiert sein müssen

.. describe:: CMake

    *Cross platform make*-Tool zum Erzeugen von Makefiles


.. describe:: Python

    Ich empfehle die Verwendung von `Python <http://python.org>`_ in
    der Version 2.7. Auf dem Roboter läuft (aktuell) noch die Version
    2.6.

    .. warning:: Neuer ist nicht immer besser. Python 3 ist nicht
       abwärtskompatibel und wird deswegen nicht mit unserem
       Code funktionieren!


.. describe:: virtualenv

    Mit `virtualenv <http://www.virtualenv.org/en/latest/>`_ lassen sich ganz
    einfach isolierte Python-Umgebungen erstellen. Wir benutzt virtualenv,
    um bei der Entwicklung unabhängig vom System bestimmte Python-Pakete
    verwenden zu könnnen, ohne die globale Umgebung zu verändern.


.. describe:: Cython

    `Cython <http://cython.org/>`_ ist eine Programmiersprache, welche die
    Entwicklung von C/C++-Erweiterungen für Python sehr einfach macht.
    Es handelt sich an eine von der Syntax an Python orientierte Sprache,
    die jedoch getypte Variablen und die Verwendung von C/C++-Funktionen
    unterstützt. Der in Cython geschriebene Code wird nach C übersetzt
    und als Python-Modul kompiliert.


.. describe:: Boost

    Für einige *low-level*-Funktionen im C++ Code wird
    `boost <http://www.boost.org/>`_ verwendet.
    Aktuell wird boost für *Shared-Memory* im Zusammenhang mit
    *inter-process communication* benutzt.


.. describe:: Eigen3

    Wir verwenden `Eigen <http://eigen.tuxfamily.org/index.php?title=Main_Page>`_
    in der Version 3 als Bibliotek für die Vektor- und Matrix-Rechnung.
    Eigen ist sehr flexibel, sehr schnell und trotzdem relativ einfach
    zu verwenden.


.. describe:: gevent

    Die Pythonbibliotek `gevent <http://www.gevent.org/>`_ ist eine
    auf `Koroutinen <http://de.wikipedia.org/wiki/Koroutine>`_ basierte
    Bibliotek zur Netzwerkprogrammierung in Python. Man kann sehr leicht
    *blockierenden* Code schreiben, der dann trotzdem mehrere Klienten zur
    Laufzeit in nur einem Thread bedienen kann.

    Gevent wird z.B. im Webinterface-Server verwendet.


.. describe:: Construct

    Hierbei handelt es sich um eine Bibliotek, die das Interpretieren
    und Schreiben von Binärdaten, wie sie in einer C-Struct stehen,
    sehr einfach macht. Mit `Construct <http://construct.wikispaces.com/>`_
    beschreibt man die Datenstruktur deklarativ, statt sie procedual zu
    zerlegen.


.. describe:: OpenCV

    OpenCV ist eine freie Programmbibliothek mit Algorithmen für die
    Bildverarbeitung und maschinelles Sehen. Sie ist für die Programmiersprachen
    C und C++ geschrieben und steht als freie Software unter den Bedingungen der
    BSD-Lizenz. Das „CV“ im Namen steht für englisch „Computer Vision“.
    Die Entwicklung der Bibliothek wurde von Intel initiiert und wird heute
    hauptsächlich von Willow Garage gepflegt.


.. describe:: Versionsübersicht

    =========== ====================
    Bibliothek  Benötigte Version
    =========== ====================
    OpenCV      2.3
    Construct   egal
    gevent      0.13.0
    Eigen3      >= 3
    Boost       >= 1.48 sollte super sein
    Cython      0.16
    virtualenv  recht egal
    Python      2.7
    CMake       2.8
    =========== ====================

