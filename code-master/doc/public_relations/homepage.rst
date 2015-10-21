========
Homepage
========

Unsere Homepage unter bit-bots.de ist unser Wichtigster Auftritt in der Öffentlichkeit.
Das ganze wird mit Wordpress administriert und ist wirklich Kinderleicht zu bedienen.
Daher ist auch jeder aufgerufen sich einen Admin-Account zu schnappen und regelmäßig über seine Tätigkeiten zu "bloggen" sowie die Seiten aktuell zu halten.


.. _seiten_vs_beiträge:

Seiten vs. Beiträge
-------------------

Seiten sind feste Bestandteile der Homepage, z.B. die Mitgliederübersicht oder die Fotosammlung.
Beiträge sind Einträge in unserem Blog.

Fotos
-----

Nichts transportiert informationen so gut wie Bilder. 
Anfang 2015 lag die Menge an Bildern auf unserer Homepage bei ca. 1500 Stück,
darum ist es wichtig zu erklären wie wir mit Fotos auf unsere Homepage umgehen.

Weniger ist manchmal mehr: Bitte versucht möglichst alles zu 
fotografieren was später von interesse sein könnte, 
aber sortiert früh und großzügig aus. 

Jedes Motiv sollte im normalfall nur 1 mal in einer Sammlung vorhanden sein.
Denkt schon beim Fotografieren daran was für Bilder ihr bevorzugt macht. 
Ein Roboter mit Ball? Hatten wir das nich schon mal...? 

Lieber ein paar weniger, dafür aber gute, symbolträchtige Fotos
(Die ihr hinterher natürlich ordentlich benennt, beschriftet und taggt!).

Plugins
'''''''

Aktuell existieren drei konkurierende Systeme zum Verwalten von Fotos auf der Homepage,
wir wollen aber nur eines davon künftig weiter nutzen. Die drei Systeme sind: 
Die builtin Mediathek von Wordpress, NextGen ein weit verbreitetes semi-komerzielles Plugin, 
WPPA ein neueres, nicht so komerziell ausgerichtetes Plugin.

Builtin Mediathek
`````````````````

.. warning::

  Bitte nicht nutzen, Bilder die hier landen fehlen in unserer Sammlung, für große
  Bildmengen nicht geeignet.

Die Standard Wordpress Funktion findet man in der Admin-Seitenleiste unter "Medien", 
bei der Bearbeitung von Seiten und Beiträgen :ref:`seiten_vs_beiträge` kann man über den 
Knopf "Dateien hinzufügen" recht kompfortabel Medien hinzufügen. 
Es ist auch möglich kleine Gallerien darzustellen. Diese werden aber **nicht** im hintergrund logisch geordnet.

Weitere Nachteile: 

  * Keine Logische Sortierung als Baum möglich
  * Kein Tagging
  * Keine Batch-Verarbeitungen (außer löschen)

Fazit:
  
  Nicht nutzen, außer ihr wollt nur mal ganz schnell ein Foto an einen Artikel hängen 
  das nicht in unserer Sammlung auftauchen soll. Wordpress erweitert dieses Feature ggf. 
  in künftigen Versionen noch, sodass 

NextGen
```````

.. warning:: 

  Nicht nutzen, deprecated!

NextGen war das erste "professionelle" Plugin das wir zur organisation von Bildern genutzt haben.
Leider existiert es in einer kostenfreien und einer "Pro" Variante, letztere kostet Geld.
Da die kostenfreie Variante nicht richtig gepflegt wurde kam es hier leider mehr und mehr zu problemen, weshalb wir uns schlussendlich für ein neues Plugin entschieden haben.

Beim export ins neue Plugin sind leider auch Metadaten (Tags, Beschreibungen) verloren gegangen, da NextGen diese in der DB speichert und niemand lust hatte ein Script zu schreiben dass diese umsetzt. (Viele unserer Bilder waren eh nicht gut eingepflegt worden)

Das Plugin ist weiter im Wordpress aktiv, da wir noch ältere Beiträge haben, 
deren Darstellung auf dem Plugin basiert. Hier ist ein Refactoring erforderlich bevor das Plugin entfernt werden kann. 

.. _wppa:

WPPA - WordPress Photo Album (Plus)
```````````````````````````````````

`Zur Plugin-Seite <https://wordpress.org/plugins/wp-photo-album-plus/>`_

Unser Aktuelles Plugin zum Sammeln von Fotos.
Es ist nicht überall schön, aber kostenfrei und ohne eine Pro-Version.
Der Funktionsumfang ist sehr groß - und es gibt eine (überwältigende) Vielzahl 
an Einstellungsmöglichkeiten.

Man kann die Fotos Taggen, Beschreiben, Bulk-Editieren, Sortieren, Suchen, Ordnen, In Artikeln als Einzelbilder oder Gallerien einfügen, eine Gesamtsammlung anlegen, Zufallsbilder oder ausgewählte Bilder in der Seitenleiste präsentieren, den Veröffentlichungsstatus der Bilder modellieren, Bilder 
Kommentieren, Bilder Bewerten, usw...

Mit anderen Worten das Plugin kann viel mehr als die Standard-Funktionen von Wordpress.
Zur Nutzung an sich gibt es einen eigenen Abschnitt :ref:`foto-nutzung`


.. _foto-nutzung:

Nutzung
'''''''

Wie erwähnt nutzen wir für die Fotos auf der Homepage WPPA :ref:`wppa`.
An dieser Stelle gehen wir mal den wahrscheinlichsten use-case komplett durch,
das hinzufügen neuer Bilder mit einem neuen Artikel.


Schritt 1: Zielalbum ermitteln / anlegen
````````````````````````````````````````

Als Erstes wollt Ihr auf "Album Admin" gehen und euch überlegen, wo 
ihr eure neuen Fotos einsortiert. 
Wenn noch kein Ort existiert legt ihr Ihn an.

Schritt 2: Fotos hochladen
``````````````````````````

Einfach unter "Photo Albums" auf "Upload" klicken und den Anweisungen folgen.
Wenn es mal probleme mit dem Upload gibt, kann auch jemand mit zugriff auf den 
Server die Bilder via SSH übertragen und dann über die "Import" Funktion in das Plugin aufnehmen.

.. hint::

  Die Schaltfläche "Upload" nicht verwechseln mit der Schaltfläche "Import" (Nur für Admins sichtbar).
  Diese dient dem Importieren von Bildern von der Festplatte des Servers.


Schritt 3: Fotos taggen, benennen, beschreiben
``````````````````````````````````````````````

Apell:
""""""
Das ist der mühsamste aber auch ein sehr wichtiger Schritt. 
Ohne sinnvolle Namen, 
Beschreibungen und Tags können Bilder von uns schlecht gefunden werden.
Dann sind sie für die Pressearbeit nichts mehr wert.

Für die Seitenbesucher sind gerade die Beschreibungstexte und Bildnamen ein 
wichtiger Redaktioneller Inhalt. Teils versteht man den Bildinhalt als Laie ohne Beschreibung nicht.

Bitte verschwendet nicht euer photographisches Talent, 
indem ihr die Bilder nach dem hochladen verkommen lasst!
Es ist natürlich nachvollziehbar dass ihr während eines Wettbewerbs 
nicht immer alles Beschriften könnt. Sorgt aber bitte dafür, 
dass dies auf jeden Fall zeitnah nachgeholt wird, 
wenn die Erinnerung an das Event noch frisch ist.

Den Arbeitsaufwand könnt ihr deutlich reduzieren indem ihr redundante und langweilige Fotos löscht noch bevor ihr sie hochladet. Macht lieber ein paar weniger Fotos und arbeitet dafür gründlich.

Vorgehen
""""""""
Am besten geht ihr über den Album-Admin auf Editieren und setzt zunächst ein mal alle Tags die für das gesamte Album gelten sollen. Dann geht ihr durch und benennt alle Fotos mit einem Sinnvollen Titel (mehrfachnennung erlaubt). Als Tags setzt ihr (kommasepariert) alles was in dem Bild zu sehen ist, z.B. "kind, tamara, knuddeln" oder "zuschauerreatkion, begeistert" etc. Auf diese Weise können wir später leicht bestimmte Bilder finden die wir suchen. Optional gebt ihr dem Bild noch eine erklärende, interessante oder lustige Beschreibung für jeden der es sich anguckt. 

Schritt 4: Fotos in Artikel einbinden
`````````````````````````````````````

Dafür nutzt Ihr am besten die Schaltfläche WPPA+ Shortcode Generator, dort könnt ihr Auswählen welche Bilder / Alben ihr in welcher Form darstellen möchtet. 
Profis können den Shortcode auch direkt in die Seite eingeben ohne die GUI zu benutzen.

.. hint::

  Die Schaltfläche *WPPA+ Shortcode Generator* ist nur im visuellen Modus sichtbar!
