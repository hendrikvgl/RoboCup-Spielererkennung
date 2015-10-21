.. _git: 

Git
===

Passt nicht gut in den Schnelleinstieg, da viele schon mit git gearbeitet haben.
Für alle anderen gibt es das hier.

Crashkurs
---------

Du hast noch nie mit Git gearbeitet?
Das sollten wir schleunigst ändern...

Was ist Git?
''''''''''''
Ein Versionierungssystem.
Git erlaubt vielen Nutzern an einem einzigen Projekt zu arbeiten und stellt bei korrekter Benutzung sicher, 
dass dabei nichts (dauerhaft) kaputt oder verloren geht. 

Einrichten von Git
''''''''''''''''''

Als erstes wird Git installiert, sofern noch nicht vorhanden::

  sudo apt-get install git

Dannach wollen wir einige grundsätzliche Configdaten setzen. 
Deine private config von git für alle projekte liegt unter:: 

  ~/.git/config

und muss ggf. noch erstellt werden.

Da rein kommen zwei wichtige Einträge::

  [user]
    name = DeinName
    email = deineKennung@informatik.uni-hamburg.de

Damit werden deine Commits gekennzeichnet, 
damit jeder sofort weiß wer du bist wenn er deine Änderungen sieht.

Es gibt weitere nützliche Werte die du später vielleicht je nach persönlichem Geschmack 
in dieser Datei eintragen möchtest. Hilfreich ist es z.B. den von dir bevorzugten Editor 
einzutragen, beispielsweise::

  [core]
    editor = vim

Weitere werte kannst du unter anderem auf `dieser Seite <http://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration>`_ finden.

Benutzen von git
''''''''''''''''

Git ist eine äußerst komplexe Software mit vielen Möglichkeiten, wie du unser git bei dir erstmalig einrichtest steht unter :ref:`git-einrichten`.
Es gibt aber ein paar Befehle die jeder Nutzer vom Git kennen muss, die erklären wir dir hier fix.

Jeder befehl von git beginnt mit einem **git** gefolgt vom eigentlichen Kommando::

  git <command>

Du kannst dir in der Kommandozeile die Hilfe dazu durchlesen mit **man** (für "manual")::

  man git <command>

Und hier die wichtigsten kommandos

.. glossary::

  git pull
    Zieht alle neuen Änderungen vom Server.
    (Ausgabe lesen, der Befehl kann Fehl schlagen)

  git add <dateiname oder pfad>
    Fügt eine bisher nicht vorhandene Datei der Versionskontrolle hinzu

  git commit <dateiname oder pfad>
    Speichert Änderungen an den Angegebenen Dateien als neue Version ab.
    (Voraussetzung ist dass die angegebenen Dateien irgendwann schon ein 
    mal mit git add hinzugefügt wurden.)
    Jede einzelne Änderung erfordert einen kurzen Kommentar,
    in dem ihr den anderen erklärt, was genau geändert wurde (und ggf. warum).
    In die erste Zeile kommt eine selbsterklärende Überschrift.

  git push
    Schiebt alle gespeicherten Änderungen auf den Server.
    Voraussetzung ist dass vorher ein erfolgreicher pull stattgefunden hat

Normalerweise legt ihr also mit **git pull** los, macht eure Änderungen, 
kennzeichnet diese mit **git commit** (evtl. **git add** bei neuen dateien) und 
schiebt anschließend alles mit **git push** auf den Server damit andere Leute 
eure Änderungen bekommen wenn sie **git pull** eingeben.

.. warning::

  Es werden schnell Leute kommen und euch zeigen wie toll es ist mit einem einzigen
  Eintrag in der Kommandozeile alle geänderten Dateien zu commiten ohne
  dass ein Editor geöffnet wird. Bedenkt dabei bitte, dass dies ein mächtiges Werkzeug ist.

  Oft hat man mehr geändert als in den commit gehört, wenn man gezielt die Dateien oder den Pfad angibt 
  ist man sich besser über die Änderungen bewusst die tatsächlich im commit landen. 
  Im geöffneten Editor wird auch noch mal angezeigt welche Dateien geändert wurden 
  und man hat einige Sekunden Zeit sich über einen guten Kommentar Gedanken zu machen.

  Der Befehl den ihr nicht benutzen sollt lautet übrigens::

    git commit -a -m Irgendwas committed

  Es dauert für euch eine Sekunde, aber es kann irgendwen anderes einen ganzen Tag kosten.


