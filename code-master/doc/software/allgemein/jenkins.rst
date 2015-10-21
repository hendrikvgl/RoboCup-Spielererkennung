Jenkins
=======

Jenkins_ ist ein Continous-Integration-Tool.
Effektiv ein Server der immer läuft, mitbekommt wenn jemand etwas neues im :ref:`git` ge-pusht hat
und dannach ein paar Standardoperationen mit dem Code durchführt.

# wird der bitbots-code gebuildet
# werden die Tests ausgeführt
# wird die Doku gebuildet und sofort veröffentlicht

Wenn es Probleme gibt werden die im Jenkins angezeigt.
Es gibt eine Consolenausgabe des jeweiligen "Build Jobs"

Der Erfolg der einzelnen Builds wird mit Rot/Blau dargestellt
und die Projektstabilität über die letzten 5 builds wird mit lustigen Icons (Sonne bis Gewitter)
illustriert.


Neuen Branch anlegen
--------------------

Jedes AG-Mitglied hat einen Benutzeraccount mit der Redmine/Mafiasi Kennung.
Die Standardbranches sind schon eingerichtet, wenn man einen neuen Feature-Branch
anlegt, sollte man folgendes machen, damit Jenkins diesen Branch auch baut:

# Einloggen
# Neuen Job anlegen (links in der Leiste)
# Namen eintragen (feature_*)
# Kopie von bestehendem Job
# Kopieren von template_feature_branch
# OK
# branches to build -> origin/\feature_"Namen"
# Speichern

Zum Testen:

# Neuen Commit auf dem Branch pushen
# Schauen, ob es gebaut wurde

Wenn man den Branch in den Master zurück geführt hat und der Branch nicht mehr
gebraucht wird, muss der Build-Job wieder gelöscht werden.

.. _Jenkins: http://www.jenkins.bit-bots.de
