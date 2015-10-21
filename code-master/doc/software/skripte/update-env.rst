Update Virtual Enviroment
=========================

Mit dem Update-env Skript können wir sich neu ergebende Abhängigkeiten unserer
Software verteilen. Wenn durch die Entwicklung neuer Features weitere Bibliotheken
oder Programme benötigt werden, dann sollte dies über diesen Update Mechanismus
geschehen. Das Update-env Skript kontrolliert die Aktuelle Version und führt dann
ggf Updates aus. Die für die Updates benötigten Befehlen stehen in der updates.sh.
Dort gibt es assozitive Arrays, die die Allgeimenen Updates und ggf Spezialisierungen
der Updates für das Chroot enthaten.
Bei diesen Skript sollte besonders darauf geachtet werden, dass keine Konflikte im
Git entstehen, da somit updaten unterdrückt werden.
