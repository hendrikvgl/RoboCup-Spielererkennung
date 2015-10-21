.. _bitbots-config:

====================
Konfigurations Datei
====================

Es gibt eine Zentrale Konfigurationsdatei unter :file:`share/bitbots/config.json`.
Diese ist im **.json** Format geschrieben und enthält sektionen für die unterschiedlichsten Module.

Darüber hinaus sucht der Ladeprozess nach einer Datei unter :file:`~/config.json` und überschreibt
damit alle Werte aus der Standard-Config.

.. hint::
  Es ist von vorteil sich eigene config-dateien anzulegen um die Standard-Config zu modifizieren.
  Man kann auf diese Weise z.B. configs für bestimmte Wettbewerbe, oder für die eigene
  Entwicklungsarbeit anlegen ohne die globale Config im Git zu verändern.
  Beispielsweise lassen sich bestimmte Module in der vision aktivieren bzw. deaktivieren.

  Zur Benutzung kopiert man die config einfach in das jeweilige home-verzeichnis.

***********
Ladeprozess
***********

Geladen werden die Configs derzeit von der funktion :func:`bitbots.util.get_config()`.
Die Funktion gibt ein dictionary-objekt zurück in dem die Einstellungen liegen.

Das ganze funktioniert nur unter python, die C-Klassen müssen die Parameter im Konstruktor bekommen.

.. hint:: 
  Wer eigene Config-Parameter hinzufügt sollte die globale :file:`share/bitbots/config.json` auf den 
  Standardwert setzen **auch dann** wenn bei fehlendem config-wert im Quellcode ein Standard gesetzt wird.
  Auf diese Weise hat man mehr überblick über die Existierenden Einstellungsmöglichkeiten.
