.. _flashen:

Flashen
=======

Unter *flashen* verstehen wir die Übertragung des fertig compilierten Quellcodes auf den Roboter.

Vorbereitung
------------

Zuerst wechselst du in das :ref:`chroot`.

Kurze Erinnerung::

  sudo bitbots-chroot/startup.sh <pfad/zu/deinem/git>

Anschließend wird der Code gebuildet::

  ~/git/build Release

Durchführung
------------

Wenn die Vorbereitung geklappt hat, dann können wir die Software auf den Roboter übertragen.
Wir müssen uns natürlich im selben :ref:`Netzwerk` befinden wie Der Roboter.
Wenn du im Bit-Bots-Nezt bist dann sollte alles klappen ::

  flash <ip oder hostname>

Du wirst noch ein paar parameter mit Enter bestätigen müssen.

Boot-Default-Parameter
----------------------

Kann man in der datei :file:`share/bitbots/boot-defaults.sh` ändern.
