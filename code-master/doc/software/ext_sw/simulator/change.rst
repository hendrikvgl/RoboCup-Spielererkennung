.. _sim-change:

Änderungen am Simulator
=======================

Der Simulator ist in lisp geschrieben.


Modell des Darwins ändern
-------------------------
Das Darwin modell besteht aus mehreren Datein TODO(endung einsetzen rng oder so).
In der Hauptdatei wird der body definiert und alle Gliedmaßen und der Kopf impotiert, welche in anderen Datein definiert sind.
Für jeden Motor brauch man ein Transform. Das Teil das dort definiert wird muss immer alle Teile welche durch diesen Motor bewegt werden beinhalten und der Motor selbst, aber nur wenn er sich bei einer Bewgung selbst mit bewegt. Also z.B. beim Knie nicht der Motor selbst, aber das Metalteil, dass nach unten geht und das Plastikteil davor. Das Teil danach wären dann die beiden Motoren im Fuß.
