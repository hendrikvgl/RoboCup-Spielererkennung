Debugging
=========

Debug programmieren 
-------------------
Mittels der Debug komponente kann man relativ einfach Log-Nachrichten und Objekte an den DebugServer / Gui schicken.

C++
"""

Hier ein kleines beispiel wie man es aus C++ verwenden kann::

    #include "parent/debug/debug.hpp"
    #include <opencv2/opencv.hpp>

    int main() {
        Debug::Scope base("Atlas");
        Debug::Scope debug(base, "Vision");
        Debug::Scope cam(debug, "Camera");
        
        debug << "Hallo" << 14 << "bla" << "und" << "so weiter";
        cam("HSV") = cv::Vec3f(1, 2.3f, 3);
        cam("HSV") = cv::Vec4f(1, 2, 3, 4);
        cam("Image") = cv::imread("photo.jpg");
        cam("BallFound") = true;
        cam("Entwickler") = "olli";
        
        Debug::Scope(base, "Vision") << "hallo";
        
        sleep(2);
    }

Python
""""""

Debug wird vorverarbeitet, so dass nur ein bestimmtes Debug level angezeigt wird.
Die Debuglevel sind:
0 Error
1 Warning
2 Important
3 Game
4 Testing
5 Debug

Aufgerufen wird es mit
debug_m(level, key, value)
oder
debug_m(level, message)

.. warning::
    Alles was folgt ist veraltet

Debug importieren::

    from Debug import Scope
    debug=Scope("Vision.Filter")

Debug Hinweis loggen(1)::

    debug << "Nachricht vom Filter"

Debug Hinweis loggen(2)::

    debug.log("Nachricht vom Filter")

Debug Warning loggen::

    debug.warn("Warnung! Bitte beachten!")

Debug Wert setzen ::

    debug.log("Eintragsname","Eintragsdaten")

Debug Scope erweitern::

    debug.sub("Erweiterungskey")

.. hint :: 
  Die Form ohne einen Wertnamen, bei der die Nachricht in der Konsole landet sollte nur 
  dann verwendet werden wenn einmalige, oder seltene Ereignisse auftreten.
  Ansonsten wird die Konsole schnell zugespammt. 
  Bei regelmäßigen Werten sollte die zweite Form genutzt werden (mit 2 parametern in python) 
  damit diese Werte in der Baumansicht landen.
  
Scope() und Scope.sub() haben sowohl in C als auch in Python einen
optionalen Parameter console_out mit default = True welcher bestimmt
ob eine nachricht auf der Console ausgegeben wird. Diese eigenschaft
wird nicht an sub-Scopes vererbt, sondern muss immer neu gesetzt werden.

Debug performanz
""""""""""""""""
Debug ist wichtig, aber oft auch teuer. 
Daher sollte man sich schon beim schreiben der debug-zeilen darüber gedanken machen
die rechenzeit des debugs gering zu halten, und das debugging optional aus zu stellen.

C++
'''
Im Ordner lib/bitbots/debug gibt es ein debugmacro unter dessen Verwendung kann zur
Kompilationszeit oder auch zur Ausführungszeit entschieden werden, welche Debug-Daten
gesendet werden. Das Macro nimmt dazu einen Parameter Level an erster Stelle und geht
davon aus, das die benutzte Variable debug heißt. Dazu muss das Macro mit
#include ../PfadZumDebugOrdner/debugmacro.h eingebunden werden.

.. code-block:: c++

    IF_DEBUG(4,{
        std::cout<<"If this prints, your debug level is >= 4\n";
    });
    DEBUG_LOG(3,"Logs a string in the console, when debug level is >= 3");
    DEBUG(2,"Example", "Logs this string in the debug-ui treeview at 'Example', when debug level is >= 2");

Je nachdem welchen Wert das Debuglevel zu Kompilation hatte, kann Debug eines hohen Levels nicht mehr gesendet werden,
da entsprechende Zeilen durch das Makro aus dem Binärcode entfernt wurden. Das setzten eines Debuglevels zur Ausführungszeit
ist da nicht so effktiv. Mit build Release -DDEBUG_LEVEL=3 wird das Debuglevel zur Kompilatiosnszeit auf 3 gesetzt.
Mit export DEBUG_LEVEL=3 bevor ein Verhalten in einer Konsole gestartet wird, setzt das Ausführungslevel auf 3 gesetzt.

Python
''''''
Unter python geht das ganze über die spezielle variable **__debug__**

.. code-block:: python

  if __debug__:
    print "If this prints, you're _not_ running python -O."
  else:
    print "If this prints, you are running python -O!"

Beim Übersetzen in den Pyton-Zwischencode werden die Zeilen entsprechend dem Wert von __debug__
optimiert und sind dann im Ernstfall nicht im weg wenn man das debugging deaktiviert.


Innerhalb der Modulstruktur gibt es nun auch die Möglichkeit, Levelabhängiges Debug zu senden.
Innerhalb des Builds werden dann Zeilen, die mit debug_m beginnen gegebenfalls zu self.debug() ersetzt oder
auskommientiert. debug_m nimmt als 1. Parameter das Debuglevel und danach die, die der normale
Aufruf von self.debug.log() bekommen würde.

.. code-block:: python

    debug_m(2, "Eine Wichtige info")
    debug_m(3, "Eine nicht ganz so wichtige Info")

wird unter DEBUG_LEVEL 2 zu folgenden Code im Virtual-Env:

.. code-block:: python

    self.debug("Eine Wichtige info")
    #debug_m(3, "Eine nicht ganz so wichtige Info")

Auf diese Weise, stören Debugausgaben, die man zum Testen und zum Entwickeln
neuer Features benutzt, nicht in Spielsituationen. Es finden weniger Aufrufe
des Debugs statt und das Netzwerk wird entlastet.
  

Debug empfangen
---------------

Nachdem die Virtual-Env eingerichtet wurde startet man einfach irgendwo den Debug-Server.::

    debug-ui
   
Debug-UI
""""""""
Hier habt ihr eine Baumansicht mit Einträgen vom Debugging die je nach Scope lexikalisch einsortiert sind.

DotView
'''''''
Mit rechtsklick auf einen Dot-Graphen-Eintrag kann man ihn sich anzeigen lassen.
Der Graph wird nur auf Anfrage mit der Space-Taste erzeugt damit man Zeit hat ihn sich anzugucken.
Dot Einträge sollten auf ".Dot" enden damit die Gui den String richtig formatiert.

ImageView
'''''''''
Rechtsklick auf einen Bildeintrag ermöglicht es das bild anzeigen zu lassen.
Man kann das Bild wieder schließen, es erzeugt aber eine Fehlerausgabe in der Konsole, welche Harmlos ist.

Debug senden
------------

Man aktiviert das Debugging mit ::

    export DEBUG=1 

Das Debugging der Vision wird extra angeschaltet mit ::

    export VISION_DEBUG=1 

Dann muss man ggf. noch die Adresse des Debug-Servers gesetzt werden sofern der nicht auf der selben Maschine läuft: ::

    export DEBUG_HOST='192.168.230.X'


