Präsentationen
==============
Im Rahmen der AG möchten wir oft Leuten zeigen was wir so machen, und was unsere Roboter so drauf haben.
Daher hier eine grobe Anleitung woran man denken sollte, was man zeigen kann, und wie das geht.

Allgemeine Tips
---------------
* Vorher Proben was man zeigen will (und gucken ob es noch läuft wie hier angegeben)
* Mit anderen Vortragenden absprechen
* Sich über das Publikum Gedanken machen (Schüler, Studenten, Professoren, Unternehmensleiter etc.) und daran anpassen. Verkleiden nützt aber nix, sei lieber du selbst.

.. important::
  Nicht aus dieser Anleitung "vorlesen", es ist kein Problem die Hälfte zu vergessen solange du
  das zeigst worauf du Lust hast und es entsprechend begeistert und flüssig rüber bringst. 
  Ein stupides Fakten rezitieren wie bei einem durchschnittlichen Stadtrundgang ist bestenfalls 
  langweilig.

Kurzvorführungen
----------------


Facedetect-Script
`````````````````

Dieses nützliche Script stellt den Darwin in eine Aufrechte Position, 
nach dem einrichten wird er am besten sicher auf einem Tisch in Publikumsnähe
platziert.

.. code::

    facedetect 

Startet das Script. 

Solange das Script (und die motion) läuft, wird der Darwin sich umgucken und versuchen 
Gesichter zu erkennen. Wird ein Gesicht erkannt, versucht der Darwin das Gesicht im Fokus zu halten. Die Augenfarbe (soweit vorhanden) wird in der Zeit auf Grün gesetzt, 
bei nicht erkanntem Gesicht Blau. 
Solange der Roboter eine Person zu erkennen glaubt, winkt er mit dem rechten Arm.
Alle 100 Sekunden wird außerdem ein neu erkannter Mensch mit "Hello Human" begrüßt.

.. hint::
    Im Februar 2014 wurde das Script auf die neuen Kameras umgeschrieben.
    Da die Alten Kamereas auf dem Kopf eingebaut wurden, hatte der Darwin mit den neuen
    Kameras zunächst Probleme Gesichter zu erkennen - und sich bei erkanntem Gesicht 
    von diesem Abgewandt, statt ihm zu folgen.
    Das Kamerabild kann mit dem Parameter --flip um 180° gedreht werden. Die Bewegung 
    des Darwin-Kopfes ist allerdings hardcoded auf korrekt herum eingebaute Kameras.

Der Demo Mode
`````````````

Wenn auf dem Roboter start-demo gestartet wird, so lassen sich einige für 
Demos nützliche Funktionen benutzen, welche hier im Folgenden aufgelistet sind:

.. hint::
  start-demo kann auch als "startup on boot" benutzt werden, dazu in */share/bitbots/boot-defaults.sh*
  demo bei dem Roboter eintragen und BOOT_ENABLED=true setzen.
  
ButtonControler
"""""""""""""""

Es gibt momentan 2 Modi im ButtonControler:

* Walking Mode
    
    Beim Walking Mode läuft der Roboter nach Drücken des Button2 los, und hält
    nach nochmaligem Drücken wieder an. Dabei wird auf langsamer Stufe (3) geradeaus gelaufen

* Animation Mode

    In diesen Mode wird durch Drücken des Button2 der Kopfstand ausgeführt.

Auswählen kann man zwischen den Modi durch Drücken des Button1 auf dem 
Rücken des Roboters.

NetworkController
"""""""""""""""""

Im DemoMode wird außerdem der NetworkControler geladen, dieser läuft parallel 
zu den, durch die Knöpfe auswählbaren, Modi. Dieses Modul lauscht auf 
Port 12345 auf eingehende UDP-Pakete um die darin enthaltenen Befehle auszuführen.
Befehle lassen sich z.B. mittels netcat senden::

    $ nc -u 192.168.230.11
    
Das Walkscript bedient sich dieser Methode zum Steuern. 
Auf der Basis des `KeyBoardControl` modules lässt sich durch Vererbung auch sehr einfach 
ein Script schreiben welches bestimmte Aktionen nacheinander ausführt::

    from keyboard import KeyBoardControl
    from gevent import sleep
    from bitbots.debug import Scope
    debug = Scope("Demo")

    class Demo(KeyBoardControl):
        def keyboard_control(self):
            self.send("play mul1")
            sleep(30)
            self.send("w")
            self.send("a")
            sleep(5)
            self.send(" ")
            self.send("play init")
            self.send("say have a nice Day")
            
    demo = Demo(debug)
    demo.keyboard_control()


Momentan verfügbare Befehle sind die Buchstaben fürs Laufen (w, a, s, d und " ")
"play name_der_animation" um die Animation name_der_animation abzuspielen
und "say text der gesprochen werden soll". 
Das Abspielen geschiet in einem Thread im Hintergrund weswegen danach mittels sleep
gewartet werden muss.

Dancepad
""""""""

Der Dancepad Controller Leitet befehle vom Dancepad welches an einem Laptop Angeschlossen
ist mit hilfe des *NetworkController* an den Darwin weiter. Um das Dancepad zu benutzen
kann man wie folgt vorgehen:

* Auf dem Roboter start-demo starten
* Auf dem Laptop mit angeschlossenem Dancepad::

    $ sudo dancepad
    
Das Script fragt jetzt nach der IP des Roboters, und versucht das Dancepad anzusteuern.
Dannach ist das Dancepad Nutzbar.

Tastenbelegung: 

* Pfeile = Laufen
* Viereck = Rechtsschuss
* Dreieck = Linksschuss
* X = Stopp
* Kreis = Handstand


Die Throw-In Challenge
``````````````````````

.. warning::

    .. deprecated :: 2014-02-27

    Funktioniert nicht mit den aktuellen Hardware-Konfigurationen.
    Der neue Kopf ist zu hoch um die Hände über den selbigen zu heben.
    
Der Roboter bückt sich um einen Ball aufzuheben und 
macht direkt im Anschluss eine Wurfbewegung
welche den Ball ein kleines Stück weit fliegen und ein noch größeres 
Stück weit rollen lässt. 
In vielen Fällen bleibt der Darwin beim Abwurf sogar stehen!

Material
""""""""

* Roboter mit Händen
* Akku (zur Not Netzteil, Akku sehr empfohlen)
* Tennisball
* Laptop
* WLAN, oder notfalls LAN-Verbindung zum Roboter

Vorbereitung
""""""""""""

* Roboter booten
* Mit dem Roboter per SSH verbinden
* Zwei consolen öffnen

  * entweder mit

    ::

      screen
      strg+a & c (für neues Fenster)
      strg+a & leertaste (zum Fenster wechseln)

  * Oder durch eine zweite SSH-Shell

Durchführung
""""""""""""

#. motion starten, 60 sek. autoabschaltung deaktivieren
  
  ::

    motion --no

#. In zweite console wechseln
#. record starten 

  ::

    record 
    load throw_in
    play

.. important::
  Darwin stützen und ihm den Ball direkt vor die Füße legen. 
  Ansonsten abwarten und ihn machen lassen.
  Er kommt auch nicht in die Ausgangsstellung zurück, weil er sonst umfallen würde.
  Deshalb ihn stützen und manuel mit dem Befehl `init` in die Ausgangsstellung bringen.

Dinge zum Erzählen
""""""""""""""""""
* Originalchallenge ist es einen Ball so weit zu werfen wie es geht.

  * Es zählt die Rollweite, nicht die Flugweite
  * Ball muss über den Kopf gehoben und so geworfen werden falls Technisch möglich
* Hände erfordern Anpassung anderer Roboterposen wie z.B. des Aufstehens 
* Darwin bleibt nach dem Abwurf meist stehen, ist aber nicht zwingend erforderlich.
* Wir haben diverse Befestigungsmethoden für die Hände getestet, unter anderem Schrauben.
  Nichts hat sich als so effektiv, stabil und haltbar erwiesen wie unser Klebeband.
* Ein Video davon haben wir auch hochgeladen

Probleme
""""""""
* Kaputte Motoren können dazu führen dass die Animation nicht mehr richtig funktioniert 

  * z.B. indem ein Arm nicht mehr hinterher kommt beim Abwurf
* Noch kippt der Roboter zwischendurch um wenn man ihn nicht festhält
* Autmatisches Aufstehen bei Umkippen ist durch die Hände behindert
