Assembly
********

Da ein Roboter aus mehreren Teilen besteht kann man diese in einer Assembly (Template Assembly Standart(DIN)) zusammen bauen.
Hierzu benutzt man links oben Place um fertige Einzelteile zu platzieren. Diese kann man dann mit einander verbinden.
Es ist sehr guter Stil (und das sollte man auch auf jedenfall mahcne) wenn das Grundobjekt an den Koordinaten Ursprung gebunden wird. Ansonsten wird man später immer Probleme mit der Perspektive haben.

Constrains
==========

Um Teile fest miteinander zu verbinden kann man Constrains benutzen. Hierbei gibt es mehrere zur Auswahl. Am wichtigsten sind Mate, Angel um Symmetrie. Mit ein bischen herumspielen findet man schnell raus wies geht. Wichtig ist, dass immer der Gegenstand bewegt wird, den man zu erst anklickt. Außerdem sollte man bedenken, dass es nicht reicht, wenn man z.B. die beiden Schraublöcher von zwei Teilen miteinander Constraint, weil man dann immer noch 2 Achsen hat um die man die Teile drehen kann. Man braucht also eigentlich immer 3 Constrains zwischen 2 Teilen um sie fest zu verbinden.


Assemble
========

Wenn man Teile die verschraubt werden verbinden will bietet sich oft Assemble an (zu finden wenn man die weiteren Schaltflächen in dem Bereich von Constraints und Joints anzeigen lässt). Assemble funktioniert im Prinzip wie der Mate-Constraint bloß, dass es einem mehr grafische Unterstützung bietet um die Constrains zu setzen. Außerdem werden wenn man zwei Löcher mit einander assembled auch noch die Flächen gleichzeitig constraint. Das bedeutet, dass man mit Assemble nur 2 (statt 3) Verbindungen erstellen muss um alle Achsen zu blockieren.

Joints
======

Wenn man Verbindungen möchte, die Beweglich sind muss man Joints benutzen. Hier gibt es auch wieder eine Auswahl an verschiedenen Joints. Um die Teile die man gejoint hat auch bewegen zu können muss man dann ein Teil per Rechtsklcik auf groundet setzen, dieses bewegt sich dann nicht mehr. Ist ein Teil der Assemlby selbst eine Assembly und es gibt in dieser Unterassembly joints die man bewegen möchte muss man diese (per Rechtsklick) auf Flexible setzen.

Create
======

Man kann mit Create direkt in der Assembly neue Teile erstellen. Dies ist sehr praktisch, besonders, wenn man zwei Teile miteinander verbinden möchte.

Edit/Open
=========

Per Rechtsklick auf ein Teil kann man dieses entweder ganz normal öffnen(Open), oder direkt in der Assembly editieren(Edit). Wenn man ein Teil editiert werden die anderen teiltransparent. Um dann wieder zurück zu kommen muss man oben rechts auf return klicken.

Content Center
==============

Es gibt in Inventor eine Bibliothek mit Standartteilen wie Schrauben, Muttern, etc. Um Teile aus dieser Bibliothek in die Assembly zu packen muss man links oben auf den Pfeil unter Place klicken und dann "Place from Content Center" klicken. Dort kann man dann das Teil auswählen.