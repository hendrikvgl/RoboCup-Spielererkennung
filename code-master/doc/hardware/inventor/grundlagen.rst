Inventor Grundlagen
*******************

Installation
============
Als Studenten bekommen wir praktischerweise alle Lizensen für das Programm :D Aber das Programm läuft leider nur unter Windows :(
Dazu muss man nur auf http://www.autodesk.com/education/free-software/inventor-professional gehen (falls der link nicht mehr funktionieren sollte nach "Autodesk Inventor Student" suchen und man findet es).

.. important::
  Wir benutzen immer Autodesk Inventor Professional 2014. Bei anderen Versionen kann es zu Schwierigkeiten kommen! Bisher haben wir immer die englische Version installiert und ich würde raten das weiterhin zu machen, weil die Begriffe sich doch sehr unterscheiden und man nach den deutschen auch wesentlich schwerer suchen kann.

Zur Installation einfach den Anweisungen auf der Seite folgen. Bisher scheint es so, als wenn man mit der gleichen Lizens das Programm gleichzeitig auf mehreren Rechnern installieren kann.


Einrichten
==========
Dann brauchen wir natürlich noch das Git mit den Datein. Da wir uns ja gerade unter Windows befinden ( :( ) müssen wir z.B. Tortoise Git benutzen. Dran denken, dass ihr entweder den private key von eurer Linuxinstallation kopiert oder extra einen key für Windows anlegen und im Redmine eintragt. Falls ihr einen neuen anlegt könnt ihr dafür den Keygen von Putty verwenden, der wird bei Tortoise direkt mit installiert.

Die Adresse für das GOAL-Git ist: gitolite@git.mafiasi.de/robocup/bitbots-hardware/goal-parts

Wenn ihr jetzt Inventor startet müsst ihr als erstes das Projekt auswählen. Dafür oben links unter dem Reiter "Get Started" auf Projects gehen. Dann Browse und die Datei GOAL, die direkt im Git liegt auswählen. Dies ist wichtig, damit ihr die anderen Datei überhaupt öffnen könnt.

Jetzt solltet ihr alle Datein im Git öffnen können


Verschiedene Datein
===================

In Inventor baut man aus mehreren Einzelteilen(.ipt) sogenannte Assemblys(.iam) zusammen. In den Assemblys kann man wiederum andere Assemblys als Teil benutzen.
Sowohl von Teilen als auch von Assemblys lassen sich technische Zeichnungen (.idw) machen.
Wichtig ist, dass wir die richtigen Templates benutzen. Diese befinden sich alle im Ornder "Metric" und sind folgende:

Aluminium Teile: Sheet Metal(DIN).ipt
3D Druck: Standart(DIN).ipt
Assemblys: Standart(DIN).iam
Technische Zeichnungen: .. todo:: eintragen
Presentation: Standard (DIN).ipn

Es gibt noch weitere Dateitypen, die wir indirekt benutzen:
.step: Format der original Darwin Teile
.dxf: Format zur Eingabe in die Fräse von Dennis Vater (eigentlich von Autodesk AutoCAD)


Inventor lernen
===============

Unter "Get Started" gibt es einige Tutorials die man sich zum anfang ansehen sollte. Desweiteren findet man im Internet auch sehr viele Informationen, da dieses Programm wirklich viel benutzt wird.
Am besten sollte man jmd fragen, der sich schon mit dem Programm auskennt und sich mit dem einfach mal ne Stunde hinsetzen. Um herauszufinden wer dafür geignet ist im People_Interface nachsehen.

.. todo:: eventuel auch ein eigenes kleines einführungsvideo wie beim Redmine machen.


"Coding Standarts"
==================

Ähnlich wie beim Programmieren sollten man sich an einige Regeln halten um das Modell übersichtlich zu halten und später auch besser veränderbar zu machen.


Variablen
'''''''''
In Inventor kann man ähnlich wie in einer Programmiersprache auch Variablen benutzen. Dies ist sehr nützlich um z.B. die Größe alle Löcher eines Teils schnell zu ändern. Das ganze funktioniert sogar Datei übergreifend. Zugriff auf die Variablen bekommt man über das kleine schwarze "f_x" ganz oben in der Schnellzugriffsleiste. Zu erst sollte man dann dort Link anklicken und die oberste Assembly auswählen (z.B. GOAL.iam) und dann die Variablen von dort linken. So werden Änderungen im gesamten Roboter umgesetzt. 
Will man eine neue Variable erstellen muss man dieses in der Assembly machen und dann diese Variable nochmal linken.
Natürlich sind auch hier namen, die Sinnergeben sinnvoll ;)

Namen und Ordner
''''''''''''''''
Die Datein sollten auch sinnvoll benamt sein. Am besten immer anfangend mit Position im Körper, also z.B. "head" und dann weiter mit einer näheren Beschreibung. Bitte keine Leerzeichen sondern Unterstriche verwenden.
Außerdem sollte das ganze sinnvoll in Ordnern angelegt werden. Also es gibt z.B. den Ordner Head, dort lege ich für einen neuen Kopftypen dann einen neuen Unterordner an wie "Head_Fancy_with_Face" wo dann die zugörigen speziellen Teile (also nicht sowas wie Motoren die auch wo anders verwendet werden) zusammen mit der Assembly Datei des Kopfes hineinkommen.

Spiegeln
''''''''
Unsere Roboter sind Humanoid und deshalb zu einer Fläche Symetrisch. Dies sollten wir auch ausnutzen und nicht zwei Beine bauen sondern nur eins und dieses spiegeln. Dies spart bei späteren Änderungen 50% Arbeit :D
Innerhalb eines Teils kann man auch durchaus noch weitere Symetrien haben. Auch einzelne Features, wie Löcher, können mehrere Symmetrien haben. Man sollte dies nach Möglichkeit immer ausnutzen.

Construction Lines
''''''''''''''''''
Wenn man in einer 2D Skizze Linien anlegen will, die keine Features definieren sollen, sondern nur z.B. die Entfernung zwischen zwei Löchern definieren sollen, sollte man Construction Lines benutzen. Dazu aktiviert man einfach unter "Sketch" -> "Format" -> "Construction"
