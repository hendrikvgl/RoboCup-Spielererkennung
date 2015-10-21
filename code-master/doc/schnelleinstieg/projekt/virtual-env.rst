.. _virtual-env:

Virtual-Env
===========

Das Virtual-Env(iroment) sorg einfach gesagt dafür, dass unser Computer denkt, dass er ein Roboter wäre und den Code
kompilieren kann, auch wenn er eigentlich ein Architektur hat.

Benutzt wird das virtual-Env für verschiedene Dinge, z.B. um den Code auf dem Rechner durchbauen zu können
und zu sehen, ob dabei Fehler auftreten. Aber auch wenn man Tools, wie die Debug-UI, benutzen will braucht man dass
Virtual-Env.

Um es zu aktivieren benutzt man folgenden Befehl:

source PFAD-ZUM-GIT/.py-env/bin/activate

Wenn man das Virtual-Env aktiviert hat kann man mit PFAD-ZUM-GIT/build Release den Code kompilieren und dann z.B.
mit dem Befehl debug-ui-neu die Debug-UI starten

Probleme
--------

Sollte das Virtual-Env aus irgendwelchen Gründen nicht starten, am besten erstmal versuchen es zu aktualisieren, indem
man das infrastruktur/setup.sh Skript ausführt.