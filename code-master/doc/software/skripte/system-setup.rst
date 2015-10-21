***************
setup-system.sh
***************

.. warning:: Dieses Programm beutzt dd! Damit kann man sich seine Festplatte
    überschreiben wenn man nicht *ganz* vorsichtig ist. Nach einschlägigen
    berichten ist es nicht soo toll die ersten 4 GB seiner Festplatte
    zu überschreiben.

Dieses Script dient dazu die Roboter/USB-Sticks mit einem neuen System zu
bespielen.

Vorgehensweise:

1. System.raw.gz runterladen: http://data.bit-bots.de/system.raw.gz
2. Wenn Updates eingespielt werden sollen: Sonst GOTO 7
3. system.raw.gz entpacken (Achtung ca. 4GB)
4. mit kvm öffnen::

    $ kvm system.raw

5. updates machen
6. system runterfahern, kvm beenden
7. Wenn der Interne Flasch des Roboters geflasht werden soll:
    a. system.raw.gz auf einein stick ziehen
    b. Roboter von einem 2. Stick Booten (Nicht vom zu flaschenden Speicher (wichtig!)
    c. 1. Stick mounten
8. Script anpassen: Den Pfad zur system.raw(.gz) in setup-system.sh anpassen
    a. Wenn ihr es vorher entpackt haben zcat durch cat ersetzen
9. Nachsehen welchers device Überschireben werden soll

    ..warning:: Aufpassen!, da gehen *alle* daten verloren

10. Script ausführbar machen::

        $ chmnod +x setup-system.sh

11. Script mit rootrechten aufruffen::

       $ sudo setup-system.sh /dev/sd*

    sd* durch das device ersetzen *aufpassen*
12. Roboternamen eingeben
13. Warten
14. Testweise vom neuen System booten
15. Bei änderungen am system.raw nach dem test wieder hochladen
