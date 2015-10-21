.. _sec_doku:

Howto Doku
**********

Dokumentieren der eigenen Arbeit ist irre wichtig. Dabei gibt es verscheidene
Formen der Doku, die im folgenden Text erläutert werden.

Sphinx Doku-System
==================

Wir benutzen das Dokumentationssystem
`Sphinx <http://sphinx-doc.org/index.html>`_, um unsere Doku zu schreiben.
Die Generierte Doku liest du gerade.

Die Dateien dafür liegen im (Software) GIT-Verzeichnis :file:`/doc`.

Die Syntax von Sphinx entspricht dem :abbr:`rst(re-structured text)`-Standard.
Die Doku dazu findet ihr auf der `Sphinx-Seite <http://sphinx-doc.org/index.html>`_, 
für das reine Markup gibt es alternativ auch Doku  
`hier <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_.



Kompilieren
-----------

Nachdem ihr die Dateien unter :file:`/doc` erfolgreich editiert habt,
testet ihr ob ihr alles richtig gemacht habt.

Dazu gebt ihr im Verzeichnis :file:`/doc` ::

	make html

ein. Sofern Sphinx korrekt installiert ist, wird das Kompilat nun in
:file:`doc/_build/html` abgelegt.

Achtet auf die Warnings und entfernt mindestens die,
für die ihr selbst verantwortlich seid.

Sobald alles sauber ist, könnt ihr das Ergebnis committen.
Die Doku auf unserem Server wird automatisch neu compiliert.

Sphinx-Builds sind inkrementell. Wenn ihr auch dateien neu builden wollt die ihr nicht verändert habt, dann benutzt bitte::

  make clean html
  
Das ist besonders wichtig wenn man warnings sehen möchte die schon vorher da waren.

.. hint::
  Für die Auto-Doku ist es erfordrerlich dass das :ref:`virtual-env` aktiviert ist.

.. _autodoc:

Autodoc
-------

Mit Autodoc lässt sich die Doku direkt aus den Python-Docstrings
im Quelltext generieren.

Die einzelnen Direktiven zum Autodoc, wie z.B.

.. code-block:: rst

	.. automodule:: moduleFoo

entnehme man der offiziellen Sphinx-Doku_.

Es sei aber erwähnt, dass die Module und Klassen, welche man mit Autodoc
importieren will, im aktuellen Pfad sein müssen. Dazu kann unter Umständen
ein Editieren der :file:`doc/conf.py` nötig sein.

.. hint::
  Module ohne .py extension können nicht mit autodoc geladen werden (z.B. aus bin/)



Sphinx Extensions
-----------------

Die Erweiterungen können bei Bedarf in :file:`doc/ext/` abgelegt werden
und müssen in die :file:`doc/conf.py` geladen werden.



Doku-Todos
----------

Um mangelhafte Doku zu markieren, könnt ihr die folgende Todo-Direktive benutzen.

.. code-block:: rst

  .. todo:: 
    **Thema**

    Aufgabenbeschreibung (markup möglich)

Das **Thema** ist gewünscht damit die Todo-Übersicht übersichtlich ist.



Aktuelle Todos
^^^^^^^^^^^^^^

Aktuell gibt es folgende Todos in der Doku:

.. todolist::



.. _Redmine: http://redmine.bit-bots.de
.. _Sphinx-Doku: http://sphinx-doc.org/ext/autodoc.html
.. _CRM-System: http://crm.bit-bots.de
