Aufbau der Software
===================

.. todo::
    Das könnte noch etwa anschaulicher und ausführlicher beschrieben werden.

Die Software besteht aus mehreren Bereichen:

:ref:`sec_motion`
-----------------

Kümmert sich um die Ansteuerung der Hardwarekomponenten und ist quasi das Kleinhirn und kümmerst sich deshalb um
Dinge wie z.B. Aufstehen.

:ref:`sec_ipc`
--------------

Lässt verschiedene Softwareteile miteinander komunizieren

:ref:`sec_libs`
---------------

Wir haben verschiedene Softwarestücke, nicht direkt selbst etwas tun, sondern von den Modulen aufgerufen werden.

:ref:`sec_mod`
--------------

Die Module sind in Python geschrieben und beinhalten den höheren Programcode. Sie kommunizieren über ein
   data-dictionary miteinander. Es gibt zwei Untergruppen:

:ref:`sec_basic`
''''''''''''''''

Diese machen Dinge wie Postprocessing der Sensordaten, Lokalisation, Kommunikation zwischen Robotern, usw.

:ref:`sec_behaviour`
''''''''''''''''''''

Diese Steuern wirklich das direkte Verhalten des Roboters, also seine Entscheidungen.

