.. _chroot:

Chroot
======

Als Chroot bezeichnet man unter Linux eine Änderung des Wurzelverzeichnisses.
Effektiv kann man ein anderes System in der Ordnerstruktur eines anderen Systems anlegen.
Der chroot-Befehl ermöglicht dann das Wechseln zu diesem System.

Bei uns benutzen wir ein System, das mit dem des Darwin identisch ist, 
um unsere Software auf unseren Laptops vorzukompilieren.
Dann müssen wir nur noch das fertige Compilat auf den Roboter :ref:`flashen`


Herunterladen und Einrichten
----------------------------

Die chroot-umgebung ist etwas groß, der Download wird einige Zeit in 
Anspruch nehmen!

Folgendes einfach in die Console kopieren:: 

  # Runterladen
  wget http://data.bit-bots.de/bitbots-chroot.tar.gz
  # Entpacken
  sudo tar xvf bitbots-chroot.tar.gz

.. hint:: 
  Das Einrichten des chroot erfordert root-rechte, 
  da wir das chroot auch nur als root-user aktivieren
  möchten.

Nutzung
-------

Im Chroot findet sich ein Aktivierungsskript, 
das die Einrichtung des bitbots-systems im 
aktuell geöffneten Terminal übernimmt.

::

  # Nutzen
  $ sudo bitbots-chroot/startup.sh pfad/zu/deinem/git

Die Kommandozeileneingabe wird dich jetzt als bitbots@<dein_host> anzeigen.
Du kannst das Chroot nun nutzen als wärest du auf einem bitbots.

Wie du jetzt buildest, und den Roboter :ref:`flashen` kannst erfährst du in der nächsten 
Lektion :)

.. _data.bit-bots.de/bitbots-chroot.tar.gz: http://data.bit-bots.de/darwin-chroot.tar.gz

LDAP Probleme
-------------

Wenn man LDAP benutzt geht das nicht, weil es Probelme mit Rechten gibt. Um das zu lösen muss man die build-Datei
anpassen und dort in der Funktion determine_build_path den Pfad aus dem git repository rausnehmen::

    BUILD_PATH=${ROOT}/../.build_${COMPILER}_${BUILD_DIR_SUFFIX}${CROSS})

.. important::
    Wichtig sind die beiden Punkte ziwschen Root und build

Bitte dann darauf aufpassen, das man diese Änderung nicht committet. Dazu: git update-index --assume-unchange build

