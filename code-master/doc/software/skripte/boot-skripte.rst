Boot-Skripte
============

Wir haben zwei Boot-Skripte, die wir standartmäßig auch undseren Robotern ausführen.
Sie werden über die boot-defaults in share/bitbots/boot-defaults.sh konfiguriert.

    Boot-Motion:

        Die Boot-Motion kann beim starten automatisch eine Motion starten.
        Diese kann eine SoftMotion sein.

    Boot-Behaviour:

        Das Boot-Behaviour bestimmt das automatische Roboterverhalten.
        Außerhalb von Spielen ist das Demoverhalten "demo" zu empfehlen.
        Die Roboterrollen werden ebenfalls über die boot-defaults konfiguriert.
        Dort gibt es ein Assoziatives Array in das für jeden Roboter das
        ausgewählte Verhalten oder demo eingetragen wird. Ein Beispielverhalten ist:
        "\"behaviour Goalie\""
