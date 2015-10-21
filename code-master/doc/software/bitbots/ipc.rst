.. _sec_ipc:

IPC
===

Die eigentliche Kommunikation mit dem Roboter wird durch einen unabhängigen
Prozess (``motion``) geregelt. Mit diesem Prozess wird mittels
`IPC <http://de.wikipedia.org/wiki/Interprozesskommunikation>`_
kommuniziert. Im folgenden gehen wir davon aus, dass wir uns
innerhalb eines Systems befinden und verwenden daher
`Shared Memory <http://de.wikipedia.org/wiki/Shared_Memory>`_.
Die :ref:`sec_ipc`-Implementierung kann jedoch auch z.B. über Netzwerk stattfinden.

Der ``motion``-Prozess liest die Stellung der Gelenke etwa achzig
pro Sekunde aus und übergibt diese der :ref:`sec_ipc` Implementierung, von der
die :class:`Pose` dann in den Shared Memory-Bereich geschrieben wird.

Andere Prozesse haben nun Zugriff auf die aktuelle Stellung der Gelenke,
indem sie die :class:`.PyPose` aus dem Shared Memory auslesen.
Dies geschieht durch die Verwendung der Klasse :class:`.SharedMemoryIPC`::

    from bitbots.ipc import SharedMemoryIPC
    ipc = SharedMemoryIPC()

    # Ausgeben der aktuellen Gelenkstellungen
    print ipc.get_pose().positions

Die Funktion :func:`~ipc.SharedMemoryIPC.get_pose` gibt ein Objekt zurück, über das die einzelnen
Gelenke abgefragt werden können. So kann die Richtung, in die der Roboter
guckt, über das Gelenk :attr:`head_pan` erfragt werden::

    # Schnappschuss des Roboters erstellen
    pose = ipc.get_pose()
    print pose.head_pan.position

Eine neue Gelenkstellung kann über das :attr:`goal`-Attribut eines Gelenks
geschehen::

    # Setze den Motor auf 30°
    pose.head_pan.goal = 30


Stellung des Roboters
^^^^^^^^^^^^^^^^^^^^^
.. module:: bitbots.robot.pypose

.. autoclass:: PyJoint

.. autoclass:: PyPose

    Das von :func:`~ipc.SharedMemoryIPC.get_pose` zurückgebene Objekt unterstützt über einige Methoden
    die Vereinfachung von Zugriffen. So kann über alle Gelenke (und deren
    Namen) iteriert werden, oder mehrere Zielwinkel gleichzeitig gesetzt werden.

    .. attribute:: positions

        Gibt eine Liste von Tupeln mit den Namen und den aktuellen
        Gelenkstellungen aller Gelenke zurück. Man kann so leicht über
        alle Gelenkwerte iterieren::

            if all(abs(pos) < 10 for name, pos in pose.positions):
                print "Der Roboter befindet sich in der Ausgangsstellung"


    .. attribute:: goals

        Ähnlich wie :attr:`positions`, jedoch für die Zielwerte der Gelenke.
        Man kann die Zielwerte mehrerer Gelenke gleichzeitig setzen, indem
        man :attr:`goals` eine Liste von Name/Wert-Paaren zuweist::

            # Kopf nach oben links gucken lassen
            pose.goals = [("HeadPan", -30), ("HeadTilt", 50)]


    .. attribute:: joints

        Gibt eine Liste von Name/Gelenk-Paaren zurück. Jedes Gelenk hat
        die Attribute :attr:`goal`, :attr:`position`, :attr:`active`
        und :attr:`speed`.


    .. autoattribute:: names

    .. automethod:: set_active(active)

    .. automethod:: update(pose)

    .. automethod:: update_positions(pose)

    .. method:: __getitem__(name)

        Alternative Methode, um auf ein beliebiges Gelenk zuzugreifen. *name*
        ist dabei der Name, wie er in :attr:`names` vorkommt. ::

            >>> pose["HeadPan"] is pose.head_pan
            True



Kommunikation mit SharedMemoryIPC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. module:: bitbots.ipc.ipc

.. autoclass:: SharedMemoryIPC(client=True)
    :members: get_pose, get_version, get_state, get_motion_state

    Mit dieser Klasse kann auf die aktuellen Daten des Roboters
    zugegriffen werden, sowie neue Zielwerte für die Gelenke geschrieben
    werden.

    Nach jedem Update der Gelenkstellungen wird eine Versionsnummer
    hochgezählt.

    .. automethod:: update(pose)

    .. automethod:: set_state(state)

    .. method:: get_accel

        Gibt ein Objekt mit den Werten des Beschleunigungssensors zurück
        ::

            accel = ipc.get_accel()
            print accel.x, accel.y, accel.z


    .. method:: get_gyro

        Gibt ein Objekt mit den Werten des Winkelbeschleunigungssensors zurück.
        Siehe auch :func:`get_accel`.

    .. autoattribute:: eye_color

    .. autoattribute:: forehead_color

    .. autoattribute:: controlable


