#-*- coding:utf-8 -*-
"""
Das gesammte Verhalten wird aus verschiedenen Modulen zusammengesetzt.
Jedes Modul erledigt dabei eine bestimmte Teilaufgabe, und stellt deren
ergebnisse dann global bereit. Die dafür nötigen vorarbeiten anderer
Module werden von diesen globalen Modulen über ein gemeinsames daten
dictonary ausgetauscht. Im :mod:`framework` werden die Abhängigkeiten
ausgewertet und alle nötigen Module in der richtigen Reihnfolge
ausgeführt.

Als Basis aller Module wird die
Klasse :class:`abstract.AbstractModule`
benutzt, dort ist auch Dokumentiert was die einzelnen Methoden der
Module tun.

.. automodule:: bitbots.modules.events
.. automodule:: bitbots.modules.modules
.. automodule:: bitbots.modules.abstract
.. automodule:: bitbots.modules.basic
.. automodule:: bitbots.modules.behaviour


"""
