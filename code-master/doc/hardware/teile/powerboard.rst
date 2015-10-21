Powerboard
**********

Das Powerboard ist für die Stromversorgung des Darwins unerlässlich. Es hat nur
wenige Bestandteile, die für das Wechseln zwischen Akku und Netzversorgung nötig
sind.



Der Netzstecker
===============

Unser Netzteil liefert 12V Strom. Wir haben originale Netzteile mit stiftartigem
und umgelötete Netzteile mit abgewinkeltem Stecker. Letzterer ist dafür gedacht
Stöße besser auszuhalten, wenn der Darwin auf den Rücken fallen sollte, während
der Stecker eingesteckt ist. Allerdings sind unsere nachgerüsteten Stecker ein
wenig zu lang und passen nicht perfekt in den Darwin, sodass es oft zu
Wackelkontakten kommt. Abhilfe schafft man, indem der Stift im weiblichen
Stecker am Darwin mit einem dünnen Schlitzschraubendreher leicht aufgeweitet
wird, sodass ein besserer Kontakt gewährleistet wird.

Langfristig wären bessere abgewinkelte Stecker sinnvoll.



Der T-Stecker
=============

Der T-Stecker empfängt bei uns den T-Stecker auf Tamya Adapter, über den die
Akkus angeschlossen werden. Der T-Stecker am Darwin ist männlich und hat kleine
Kontaktbleche, die den Stecker unter Spannung halten und den Kontakt
gewährleisten. Diese Kontaktbleche können mit der Zeit verbiegen und müssen dann
wieder leicht aufgebogen werden, um Wackelkontakten vorzubeugen.

Ein derartiger Wackelkontakt wird häufig fälschlicherweise auf den Adapter
geschoben.

.. warning::
    Beim Aufbiegen der Stecker unbedingt jegliche Stromversorgung unterbrechen
    um Kurzschlüsse zu vermeiden.



Der Stromschalter
=================

An, Aus. Mehr gibt es da eigentlich nicht zu sagen. Bisher hatten wir mit dem
Schalter nie viele Probleme. Es kann aber passieren, dass der Darwin so
ungünstig fällt, dass er sich mit seinem eigenen Stromkabel den Stromschalter
ausschaltet.



Die Elektronik
==============

:download:`Schaltplan <downloads/Powerboard.pdf>`

Auf dem Board ist nicht viel spannendes drauf. Es gibt einen *MOSFET*, der den
Strom zwischen Akku und Netzteil umschaltet. Wird der Netzstecker
kurzgeschlossen, während der Darwin am Akku hängt (z.B. beim versuch den Stecker
aufzuweiten), dann schmort sofort der *MOSFET* durch und schützt damit
hoffentlich die restliche Hardware.

.. note::
    Laut Schaltplan ist der MOSFET ein "IRLR7833", in Wirklichkeit ist aber ein
    "IRLR024N" eingebaut.
