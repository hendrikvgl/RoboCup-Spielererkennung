========
Debug-UI
========

In der Debug UI kommen die daten die mit dem debuging versendet werden
an und werden angezeigt. Außerdem Speichert die Debug-ui alle
ankommenden daten in einem .gz unter /tmp/debug-<timestamp>.gz
diese Dateien lassen sich als argument an die debug-ui übergeben,
sie werden dann abgespielt.

Die Deugdaten die auf dem Darwin im Homeordner angelegt werden
können nicht so einfach abgespielt werden da es sich dabei um raw-daten
handelt. Diese können mittels::

    export DEBUG=1
    replay-debug /pfad/zur/datei.tar.gz

Wieder abgespielt werden.

.. automodule:: debuguineu.mainwindow
