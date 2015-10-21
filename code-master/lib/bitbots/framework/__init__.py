#-*- coding:utf-8 -*-
"""
Framework
^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 8.1.14: In eigenes Modul gebaut (Nils Rokita)

Das Framework kümmert sich um die ausführung der einzelnen Verhaltensmodule.
Dafür imporiert es die Module, löst abhängigkeiten auf, und Instanziiert die
Klassen.

In Runtime wird dann die entwprechende Laufzeitumgebung dafür bereitgestellt.

.. automodule:: bitbots.framework.runtime
.. automodule:: bitbots.framework.module_service
.. automodule:: bitbots.framework.event_framework
"""

from bitbots.framework.runtime import Runtime
