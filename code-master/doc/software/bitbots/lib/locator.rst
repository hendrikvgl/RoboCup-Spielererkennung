.. _locator:

Lokalisation
============

Die Lokalisation unserer Roboter basiert aus dem Verarbeiten der
ausgewerteten Bilder der Vision und dem Tracken der Roboterbewegung.
Der Lokator benötigt die Informationen über Zusammenhangskomponenten der
weißen Feldlinienpunkte, die Roboterpose und der Roboterbewegung seit dem
letzten Update.

Aus diesen Informationen kann der Roboter eine bis auf Spiegelsymmetrie
eindeutige Position bestimmen. Wenn er zusätzliche Informationen hat, wie
zu Beispiel "Ich bin in meiner Hälfte, da gerade Anstoß ist", ist eine
Eindeutige Lokalisation möglich. Solange diese nicht verloren geht, kann
der Roboter seinen Standort exakt bestimmen.

Das Locator modul bietet bisher die errechnete Position an. Diese wird
momentan noch nicht mit Zusätzlichen Informationen versehen, die aufschluss
darüber geben, wie gut diese Schätzung ist. Die Position ist ein
Dreidimensionaler Vektor. Dabei sind die ersten beiden Komponenten die
Koordinaten im Feld und die dritte ist die Drehung zur x-Achse in
Radiant. x und y sind metrisch. Der Koordinatenursprung liegt im
Mittelkreis. Die x-Achse ist die Längsseite, die y-Achse die
Breitseite. Das eigene Tor steht an der x-Position -3. Die linke
Strafraumecke des eigenen Tores mit Blickrichtung Mittelkreis liegt
an der Position (-2.4,1.1). Damit sollte das dem Feld zu grunde liegende
Koordinatensystem hinreichend beschrieben sein.

Bei der BallInfo gibt es die Parameter u,v. Dabei beschreibt u die Entfernung des
Balls nach vorne und v die Entfernung des Balls nach links, betrachtet vom lokalen Koordinatensystems
des Roboters.