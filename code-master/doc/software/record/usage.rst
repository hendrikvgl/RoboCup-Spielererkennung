===================
Record-UI Benutzung
===================
Die Record-UI dient zum erstellen von Roboteranimationen nach dem Keyframe-Verfahren. 
Dafür kann der Roboter selbst als Eingabegerät benutzt werden um die einzelnen
Schlüsselpositionen des Roboters zu ermitteln die in einer Animation erreicht werden sollen.
Die Animationen können mithilfe der record-UI verändert werden.

Normalerweise läuft die Record-UI direkt auf einem Roboter, zu dem man via *SSH* verbunden ist.

Vorbereitung
""""""""""""

* Roboter booten
* Mit dem Roboter per SSH verbinden
* Eine Motion sollte laufen (z.B. existierende soft-motion)

.. hint:: 

  Es kann sein dass bei Nutzung der screen-umgebung die 
  Darstellung der Record-UI negativ beeinträchtigt wird. 
  Es bietet sich an ein extra Terminal für die Record-UI zu nutzen.

Starten
"""""""

#. In *frische* Konsole (auf dem Roboter) wechseln
#. **record** eingeben, es öffnet sich die Hauptansicht

Aufbau der Nutzeroberfläche
"""""""""""""""""""""""""""

Der grobe Aufbau der Nutzroberfläche gliedert sich in der Folgenden Reihenfolge von
oben nach unten:

.. describe:: Kopfzeile

  In der Kopfzeile stehen ein paar Informationen wie die wichtigsten Tastenkürzel,
  und ein paar Metadaten zu der aktuell bearbeiteten Animation. 
  Das sollte sich mit der Zeit von selbst erklären.

.. describe:: Keyframeansicht (oder andere Ansichten)

  Darunter folgt ein Raum für Ansichten, der normalerweise von der 
  Liste aller Keyframes eingenommen wird. 
  Diese ist beim Start zunächst noch leer 
  (Eine freundliche Büroklammer begrüßt dort den Nutzer).

  Die Framelist ist, wenn sie entsprechen voll ist, 
  mit der Tastatur nach oben und unten scrollbar, der Inhalt 
  passt sich automatisch der Verfügbaren Terminalbreite an.
  Ob noch weitere Keyframes außerhalb des Sichtfelds des Nutzers 
  liegen zeigen im Bedarfsfall *Scrollindikatoren* am oberen bzw. 
  Unteren Rand der Keyframeansicht an. Der *cursor* 
  muss sich zum scrollen innerhalb dieser Ansicht befinden.
  
  An stelle der Frameliste werden zeitweilig auch andere Views angezeigt,
  z.B. die HelpView, die MotorView oder die MetaView.

.. describe:: Konsole

  Durch eine Trennzeile von der Keyframeansicht abgegrenzt, 
  befindet sich im unteren Bereich die Konsole.
  Es gibt einen mehrzeiligen Ausgabebereich, 
  der bei Bedarf ebenfalls gescrollt werden kann (meist ist das nicht nötig).

  Die letzte Zeile der Konsole ist die Eingabezeile die mit einem **>_** beginnt. 
  das **>_** wird als Markierung für Nutzereingaben verwendet.

  Die Konsole ändert ihre Größe automatisch, je nachdem ob sich 
  der Cursor in der Konsole oder außerhalb befindet.

  mit :kbd:`:` kann aus den meisten Ansichten in die Konsole gewechselt werden.
  mit :kbd:`ESC` kommt man aus der Konsole wieder raus.

Weitere UI-Elemente
"""""""""""""""""""

.. describe:: Keyframe

  Ein Element der Keyframeliste.
  Jeder Keyframe enthält Nummerierte Felder für alle Motoren, 
  plus je eines für Geschwindigkeit und Pause.
  Enthält ein Feld ungültige Daten, wird die Überschrift rot.
  
  Roboter können unterschiedliche Motoren enthalten. 
  Alle Motoren die in einem Roboter nicht vorhanden sind sollten auf **IGNORE** stehen.
  Aber auch vorhandene Motoren können mit der eingabe eines einzelnen :kbd:`i` auf **IGNORE**
  gesetzt werden. Sie werden dann während einer Animation nicht berücksichtig und können
  ggf. von anderer Stelle gesteuert werden.
  Mit :kbd:`DEL` kann man ein Feld komplett leeren um etwas neues einzugeben.

  Zur Navigation können die Pfeiltasten, oder die aus *vim* bekannten Tasten genutzt werden.
  mit :kbd:`TAB` kann man innerhalb eines Keyframes von Feld zu Feld springen, 
  :kbd:`n` sprint zum nächsten Keyframe.
  Auch :kbd:`Bild-Auf` bzw. :kbd:`Bild-Ab` können genutzt werden.

.. describe:: MetaView
  
  Zeigt und ermöglicht die Bearbeitung von Metadaten (Autor und Description)
  siehe Befehl :ref:`meta <re_cmd_meta>`

.. describe:: MotorView
  
  Zeigt die Position der Motoren mit ihrer Nummer in einer Grafik.
  siehe Befehl :ref:`motors <re_cmd_motors>`

Tastenkürzel
""""""""""""

Innerhalb der Keyframeliste
'''''''''''''''''''''''''''

Außerhalb der Konsole ist die Steuerung Hotkeybasiert. 
Folgende Tasteneingaben sind möglich:

- :kbd:`:` bewirkt Wechsel in die Konsole

- :kbd:`n` bewirkt Sprung ins erste Feld des folgenden Keyframes

- :kbd:`TAB` bewirkt Durchwechseln der Felder innerhalb eines Keyframes

- :kbd:`h`, :kbd:`j`, :kbd:`k` und :kbd:`l` entsprechen den Pfeiltasten 

- ←,↑,→ und ↓ bewirken normale Navigation 

- :kbd:`g` springt zum ersten Keyframe

- :kbd:`G` springt zum letzten Keyframe

- :kbd:`DEL` leert das Feld unter dem Cursor

- :kbd:`m` schaltet die Motorenübersicht an bzw. aus

Innerhalb der Konsole
'''''''''''''''''''''
- :kbd:`ENTER` bestätigt die Eingabe

- Mit :kbd:`ESC` verlässt man die Konsolenansicht

- :kbd:`TAB` Ermöglicht es Befehle, und Teilweise sogar Parameter zu vervollständigen

-  ↑ bzw. ↓ ermöglicht es vorige eingaben in die Eingabezeile zu übernehmen

- :kbd:`SHIFT` + ↑ bzw. :kbd:`SHIFT` + ↓ erlaubt es den Fokus zwischen Eingabe und Ausgabebereich
  zu verschieben.


Blitztutorial
"""""""""""""
.. warning:: 
    Es wird davon ausgegangen dass eine grundsätzliche Sicherheitseinweisung für die
    Arbeit mit dem Roboter erfolgt ist. Die Motoren sind stärker als man glaubt.

Einfach mal loslegen? 
Versuch mal folgende Befehle::

    init

Der Roboter sollte sich nun eine aufrechte Haltung annehmen.
Stell ihn ggf. auf die Füße und guck dass er gerade steht. 

::
    
    record

Jetzt sollte in der Liste der Keyframes der erste Keyframe aufgetaucht sein,
der halbwegs identisch mit der init-pose ist.

::

    off LArm

Der Linke Arm des Roboters sollte nun ohne Gewalt leicht beweglich sein.
Bring ihn in eine Position die dir gefällt während du folgendes eingibst::

    on LArm 

Die Motoren am Arm sollten jetzt wieder "hart" sein und der Roboter behält seine Position ohne Unterstützung.
Alternativ kannst du den Parameter *LArm* weglassen, dann werden jeweils alle Motoren des Roboters 
aus bzw. an gestellt.

::
    
    record

Jetzt haben wir unseren Zweiten Keyframe, mit einer veränderten Armposition.
Mit dem folgenden Befehl kannst du die Animation die du gerade erstellt hast abspielen::

    play

Herzlichen Glückwunsch! Deine erste Roboteranimation! 
Du kannst jetzt versuchen weitere Keyframes hinzu zu fügen, 
diese zu kopieren oder verschieben, einzelne Werte an den Keyframes zu ändern, 
z.B. **DUR** für die Geschwindigkeit oder **PAU** für eine Pause nach dem Keyframe.


Befehlsübersicht
""""""""""""""""

Über ::

  help commands

kann man im record-script die verfügbaren befehle auflisten lassen.

.. option:: append <name>

  Lädt die Animation *name* und fügt sie an die bestehende Animation an.

.. option:: author [name(n)] 

  Wird ein oder mehere Namen gegeben, so werden diese als Autoren der 
  Animation in den Metadaten gesetzt. Wird kein Parameter gegeben,
  so wird der aktuelle Wert des Felds ausgegeben.

.. option:: desc [Text]

  Wenn Text gegeben ist, wird dieser als Beschreibung zu der Animation gesetzt.
  Andernfalls wird der derzeitige Beschreibungstext ausgegeben.

.. option:: on [Motor|Motorgruppe]

  Schaltet einen Motor, oder eine Motorgruppe auf *fest*.
  Oder alle Motoren, wenn unterspezifiziert.

.. option:: off [Motor|Motorgruppe] 

  Schaltet einen Motor oder eine Motorengruppe auf *lose*.

.. option:: id <MotorTag>

  Gibt eine Liste der Motor-ID's aus die zu dem gegebenen *MotorTag* gehören

.. option:: init 

  Alle Motoren werden in die Initpose(Ausgangsstellung) gefahren, 
  so dass der Darwin aufrecht stehen kann.

.. option:: load <Dateiname> 

  Lädt eine Animationsdatei im .json-Format. 
  Wird die datei im Homeverzeichnis ~ 
  nicht gefunden, wird die Datei unter :file:`bitbots/share/darwin/animations` 
  Der Dateiname muss *ohne* die Endung .json eingegeben werden.

.. option:: play [auswahl] [name]

  Spielt die aufgenommenen oder geladenen Stellungen/Posen ab. 
  Wird ein Animationsname angegeben, so wird die Animation mit diesem 
  Namen geladen und abgespielt.
  Es ist außerdem möglich eine spezielle auswahl zu treffen welcher Teil der 
  Animation gespielt werden soll. Eine Auswahl kann folgendermaßen aussehen:
  **1,3-5,7** würde z.B. nur die Keyframes 1, 3 bis 5 und 7 abspielen und die 
  Keyframes 2 und 6 sowie alle die evtl. auf 7 folgen ignorieren.

  ..hint:: 

    Die Erkennung der Parameter ist halbwegs intelligent, sodass beide, oder jeweils 
    nur einer gegeben werden können. Werden beide Parameter gegeben, ist die Reihenfolge 
    einzuhalten. Animationsnamen die dem Auswahlpattern entsprechen sollte man vermeiden.

.. option:: record

  Hängt die aktuelle Pose an die Liste der Keyframes dran.
  Außerdem wird ein backup der neuen animation in :file:`~bitbots/backup.json` gespeichert.

.. option:: dump <name> 
  
  Speichert die akutelle animation unter dem namen *name.json* im Homeverzeichnis.
  (Ein Dateipfad kann derzeit nicht angegeben werden).

.. option:: revert [keyframe] 

  Löscht die letzte Stellung/Pose.
  Wird eine Keyframenummer als argument angegeben, so wird dieser Keyframe entfernt.
  Die Nummerierung wird sofort für alle Frames neu berechnet.

.. option::  clear 

  Löscht die komplette aktuelle animation.
  Die daten bleiben aber zunächst in der :file:`~bitbots/backup.json` erhalten.


.. option:: loglevel [int]
  
  Gibt die möglichkeit einen Loglevel für die GUI zu setzen und gibt kontrolle über
  die Menge der Nachrichten die in die Konsole geschrieben werden.
  Wird kein Loglevel angegeben so wird der aktuelle level ausgegeben.
  Valide Loglevel in python liegen zwischen 0 und 50, wobei 20 (logging.INFO) der
  default-wert ist. Alle normalen User-Ausgaben haben den loglevel 20, alles darunter
  sorgt für zusätzliche ausgaben.

.. option:: copy <from> [to]

   Kopiert den angegebenen frame und fügt ihn an angegebener Stelle ein.
   ein. Wird kein Ziel angegeben, so wird der Frame an Ort und Stelle kopiert.
   Der Frame der sich ggf. an der Zielposition befindet wird nach hinten geschoben.

.. option:: move <from> <to>

  verschriebt angegebenen Frame an die Angegebene Position. 
  Der Frame beim Ziel wird dabei nach hinten verschoben wenn er existiert.
  Existiert die Ziel-ID nicht, wird der Frame einfach hinten angehängt.

.. option:: help [topic]
  
  Gibt Hilfestellung zu einem Thema.
  Bisher sind die Beschreibungen der Kommandos verfügbar.
  
.. option:: pose <frame>

  Lässt den Roboter die Position des angegebenen keyframes einnehmen.
  Die Geschwindigkeit des Frames wird dabei ignoriert.

.. _re_cmd_motors:
.. option:: motors <motorgruppe>
  
  Gibt eine Übersicht über die existierenden Motoren aus.
  Gibt man als Zusatzparameter eine Motorgruppe/ einen Motornamen, 
  z.B. "Hips", "RArm" oder "LAnkleRoll" an, so werden die betroffenen
  Motoren in der Ansicht hervorgehoben.

  .. hint:: die Ansicht ist derzeit nur für den Darwin-OP implementiert.

.. _re_cmd_meta:
.. option:: meta
  
  öffnet das Editierungsfenster für Metainformationen.
  Autor und Description können verändert werden.
  Mit Enter werden alle Eingaben übernommen, ESC bricht die eingabe ab.
  Mit Tab kann man von Autor zu Description durchwechseln.
  Klickt man mit der Maus auf die Konsole, so wird die Eingabe übernommen.

  Alle Änderungen der Metainformationen werden erst nach dem dumpen der
  Animation dauerhaft übernommen. (bzw. im automatischen backup)

.. option:: mirror <keyframe> <MotorTag>
  
  Ein überaus nützlicher Befehl der einen Keyframe symetrisch machen kann.
  Dazu gibt man im ersten Parameter die Keyframenummer an, 
  in der eine symmetrie erzeugt werden soll. Es ist auch möglich *all* anzugeben
  um die Operation nacheinander für alle Keyframes zu wiederholen.
  Im zweiten Parameter gibt man ein MotorTag an, das gespiegelt werden soll. 
  z.B. *LArm* würde die Position aller Motoren des linken Arms auf die des Rechten 
  projezieren. *Right* hingegen würde alle Positionen der Rechten Körperhälfte auf 
  die Linke Körperhälfte übertragen.

.. option:: undo [n]

  Macht die letzten *n* Aktionen rückgängig die zuletzt die Animation verändert haben.
  Defaultwert für *n* ist 1. 

.. option:: redo [n]

  Wiederholt die letzten *n* Aktionen die rückgängig gemacht wurden.
  Defaultwert für *n* ist 1. 

.. option:: quit

  Beendet die Record-UI. Außerhalb der Konsole 
  kann man alternativ auch :key:`q` drücken.



Motor und Motorgruppen
""""""""""""""""""""""
Arme:

* RShoulderPitch = ID 1
* LShoulderPitch = ID 2
* RShoulderRoll = ID 3
* LShoulderRoll = ID 4
* RElbow = ID 5
* LElbow = ID 6

Hüfte:

* RHipYaw = ID 7
* LHipYaw = ID 8
* RHipRoll = ID 9
* LHipRoll = ID 10
* RHipPitch = ID 11
* LHipPitch = ID 12

Knie:

* RKnee = ID 13
* LKnee = ID 14

Fuss:

* RAnklePitch = ID 15
* LAnklePitch = ID 16
* RAnkleRoll = ID 17
* LAnkleRoll = ID 18

Kopf:

* HeadPan = ID 19
* HeadTilt = ID 20

Gruppen:

* Arms = beide Arme
* RArm = kompletter rechter Arm
* LArm = kompletter linker Arm
* Hips = komplette Hüfte
* RHip = nur den rechten Teil der Hüfte
* LHip = nur der linge Teil der Hüfte
* Legs = beide Beine
* RLeg = komplettes rechtes Bein
* LLeg = komplettes linkes Bein
* Knees = beide Kniee
* Feet = beide Füsse
* RFoot = kompletter rechter Fuss
* LFoot = kompletter linker Fuss
* AnklePitch = beide Füsse nach unten und oben bewegbar
* AnkleRoll = beide Füsse nach rechts und links bewegbar
* Head = ganzer Kopf


vorhandene Stellungen/Posen/Bewegungen
""""""""""""""""""""""""""""""""""""""

* aufstehen_left
* bottom-up
* brucelee
* freddy
* front-up
* getball[2,3,4,5]
* goalie_center_to_left
* goalie_grund[2]
* goalie_init2
* goalie_left[1,2]
* goalie_left_shoulder
* goalie_mitte[1,2]
* goalie_mitte_shoulder
* goalie_right[1,2,3]
* goalie_right_shoulder
* goalie_right_to_left
* goalie_side
* goalie_walkready
* hi = kurze Verbeugung
* init = Initialisierungszustand
* int
* lie-down
* lie-up
* lk = Kick mit dem linken Fuss
* l-pass = passen mit dem linken Fuss
* mul1 = Kopfstand
* no = Kopf schütteln
* ok = nicken mit dem Kopf
* pickup
* pushup
* rk = Kick mit dem rechten Fuss
* r_kick[1,2]
* rollover
* rollover_standup
* r-pass[1] = passen mit dem rechten Fuss
* sit-down
* spagat
* stand-up = steht auf
* strike
* talk1 = Bewegung mit Händen und Kopf(wie bei einer Rede)
* talk2
* throw[2,3,4,5,6,7,8]
* throwin
* throw_in = (funktionierender) Einwurf
* toe2
* toor2
* tor[1,2,3,4,5]
* walkready = stellt sich in eine laufbereite Position

