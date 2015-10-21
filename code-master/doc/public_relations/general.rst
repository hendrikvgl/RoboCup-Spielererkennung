Allgemeines
===========


Gource
------
Es ist toll wenn es für Presse und Besucher auf unseren Systemen nach "Arbeit" aussieht.
Statt einer Dolly-Buster animation ist also eine Gource-Animation auf dem Schirm vielleicht angebrachter. Dann kommen Leute an und Fragen was das eigentlich ist und man kommt ins Gespräch.

Im Repository unter *share/stuff/gource* finden sich diverse run-scripte für gource animationen.
z.B. "eindhoven.sh" welche bei ausführung unsere codeentwicklung während der WM in Eindhoven visualisiert.

Diese Scripte starten sich selbst immer wieder neu (reagieren so auf Änderungen im Git) 

Bildschirmschoner
"""""""""""""""""
Man **kann** in der tat gource als Bildschirmschoner einsetzen, wenn man weiß wie. 
Google hilft einem da erstaunlich wenig weiter (Stand Jan 2014) aber ich erkläre wie es geht:

xscreensaver
````````````
Im prinzip muss man nur die datei *~/.xscreensaver* editieren (falls sie nicht existiert vorher ein mal xscreensaver-demo ausführen) und folgendes in der Sektion "Programs" hinzufügen::

  "Gource"  /bin/bash             \
            /absoluter/pfad/zum/git/share/stuff/gource/all.sh   \
                      --xscreensaver          \n\

Anschließend steht einem "Gource" als visualisierung im xscreensaver zur verfügung.

Hintergrund:
************
Der Screensaver kann jedes Programm anzeigen, dass in der Lage ist in ein Fremdes Fenster zu zeichnen. In diesem Fall in das Window mit der ID **$XSCREENSAVER_WINDOW**. Gource selbst ist dazu zwar eigentlich nicht in der Lage, `wie die Entwickler bedauern <http://code.google.com/p/gource/issues/detail?id=6>`_ - allerdings benutzt Gource SDL als Bibliothek und das ist tatsächlich sehr wohl in der Lage sämtliche Inhalte für Bildschirmschoner zur verfügung zu stellen. Alles was man tun muss ist die Environment-Variable **SDL_WINDOWID** zu exportieren und dabei auf den Wert der Env-Variable **$XSCREENSAVER_WINDOW** zu setzen.

gnome-screensaver
`````````````````
Der gnome-screensaver kann theoretisch das selbe wie der xscreensaver. 
gerüchteweise gibt es sogar ein script um die xscreensaver config für gnome-screensaver zumzuwandeln.
Bisher wurde das aber noch nicht gemacht, also 

.. todo:: 
  Erklärung schreiben: Gource im gnome-screensaver einrichten 
