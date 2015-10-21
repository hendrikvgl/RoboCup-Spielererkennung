Aluminium Teile
***************

Viele der Teile in unserem Roboter sind gebogene Aluminiumbleche. Um diese richtig zu produzieren müssen wir einiges beachten.

Material
========

Unter "Sheet Metal"  -> "Sheet Metal Defaults" können wir das Material und die Dicke einstellen. Die standarteinstellungen sind:

Material: Aluminium 6061
use Thickness from Rule: No
Thickness: 2mm

Die Dicke des Teils kann auch mal auf anderen Werten liegen, wenn das gewünscht ist. Dennis Vater kann sehr gut 2 und 3mm herstellen. 1,5mm und 5mm sind auch manchmal möglich. Alles andere ist schon schwieriger.


Biegungen
=========

Es gibt grundsätzlich zwei Möglichkeiten um eine Biegung gut zu modelieren.

Zwei Skizzen
''''''''''''

Wenn man zwei 2D Skizzen macht und diese sich die Kante an der gebogen wird teilen erstellt Inventor automatisch die Biegeung sobald man den Skizzen Faces gibt. Dies ist praktisch weil man dann direkt die Skizze anpassen kann ohne das etwas umständliche Flanglmenü.
Man kann auch eine neue 2D Skizze an einem Face anfangen lassen und die Kante dann mit "Project Geometrie" erhalten und von dort aus eine neue Skizze machen.

Flange
''''''
Wenn man schon ein fertiges Face hat und dort eine Biegung anbringen will kann man unter "Sheet Metal" -> "Create" -> "Flangl" eine Fläche erstellen, die an einer Kante des bereits bestehenden Teils liegt.


Nachträglich einfügen
'''''''''''''''''''''
Wenn man nicht direkt den Bend drin hat kann man es mit "Sheet Metal" -> "Create" -> "Bend" versuchen. Allerdings ist dies nicht immer von Erfolg gekrönt.


Flache Version anziegen
=======================

Indem man auf "Sheet Metal" -> "Flat Pattern" clickt kann man sich das Teil in der ungebogenen Version anzeigen. Aber vorsicht hier können keine Änderungen gemacht werden, die dann zurück in das gebogene Teil gehen :(
Allerdings lässt sich hier gut sehen, ob man alles richtig gemacht hat. Falls das Flat Pattern garnicht erst angezeigt wird, weil man ein unbiegsames Teil Konstruiert hat sollte man sich nochmal überlgen, ob das überhaupt so möglich ist.
Wird das Flat Pattern angeziegt sollte man dadran kontrollieren, ob alle abgebogenen Flächen von der Biegekante aus mindesten 10mm lang sind, weil sie sich sonst nich biegen lassen.
Außerdem sollte man schauen, ob sich die teile beim Beigen gegenseitig behindern können und sonst entsprechende Anpassungen vornehmen.


Für CNC Fräse exportieren
=========================

Um das Metalstück von einer CNC-Fräse schneiden zu lassen lässt man sich das Flat Pattern anzeigen und macht einen neuen Sketch auf der Oberseite. Dieser sollte dann automatisch alle Features von dem Teil haben. Dann verlassen wir den Sketchmodus und klicken den Sketch im Navigator links mit rechts an und exportieren ihn als .dxf datei. Dazu machen wir dann noch eine technische Zeichnung in der wir die Biegekannten und die Metaldicke annotieren und geben das dann Dennis Vater.
