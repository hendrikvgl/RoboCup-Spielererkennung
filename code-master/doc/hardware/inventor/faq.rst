Häufige Probleme
****************

Datein öffnen
=============

Referenz zu einem Standartbauteil kann nicht aufgelöst werden
-------------------------------------------------------------

Wenn der Name des Teils mit etwas wie ISO oder DIN anfängt handelt es sich vermutlich um ein Teil aus dem Content Center.
Hierzu überprüfen ob unter "Get Started" -> "Projects" das Projekt GOAL ausgewählt ist und dort unter "Folder Options" -> "Content Center Files" der Ordner "pfad_zum_git/Library/CostomeContentCenter" ausgewählt wurde.
Falls das Problem immer noch nicht behoben wurde kann man eine neue Assembly öffnen und dort "Place from Content Center" aufrufen und das Bauteil, das fehlte, z.B. ISO 4762 suchen. Dann platzieren und dabei die richtige Größe auswählen, also z.B. M2,5*6. Danach dann nochmal versuchen die Datei zu öffnen. Falls jetzt ein anderes Teil nicht referenziert werden kann das ganze nochmal machen.

Konstruieren
============

"No unconsumed Sketches"
------------------------
Erhält man diese Nachricht, wenn man z.B. ein Face erstellen will, dann hat man wahrscheinlich eine Skizze editiert, aber keine ganz neue angelegt. Am besten einfach eine neue Skizze auf der gleichen Fläche anlegen, die andere Skizze sichtbar machen mit "Rechtsklick" -> "Visibility" in der Teile übersicht links (ist vermutlich ein Unterpunkt von einem anderen Face) und dann "Project Geometrie" benutzen.
Danach sollte man auf dem neuen eigenständigen Sketch die Operation aufrufen können.

Assembly
========

Teile lassen sich nicht bewegen
-------------------------------

Als erstes überprüfen, ob ein Teil (und nicht alle) als "Rechtsklick" -> "Grounded" gesetzt ist. Ansonsten gibt es keinen festen Bezugspunkt für die Bewegung.
Versucht man ein Subteil eines schon zusammengesetzen Teils zu bewegen (also ein Teil einer Subassembly) muss man diese auf "Rechtsklick" -> "Flexible" setzen.


Constrains schlagen fehl
------------------------

Wenn Constrains sich nicht setzen lassen liegt das oft daran, dass man sich bei den Löchern der original Darwinteile Verklickt hat. Diese sind trichterförmig und wenn man nicht den äußersten Ring auswählt funktioniert es nicht.
Ansonsten kann man auch mit dem Offsetwert versuchen das Problem zu lösen in dem man dem Constraint etwas Spiel gibt.
