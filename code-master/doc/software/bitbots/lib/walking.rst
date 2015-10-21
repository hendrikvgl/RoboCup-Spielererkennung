Walking Engine
==============

.. class:: walking.WalkingEngine

    Die WalkingEngine stellt auf einfache Art und Weise Funktionalität bereit,
    um den Roboter laufen zu lassen. Dafür reicht es, eine Instanz der
    Klasse zu erzeugen, die gewünschte Laufrichtung festzulegen
    und alle acht Millisekunden nach einem Aufruf von :func:`process`
    die aktuelle Stellung der Gelenke auf den Roboter zu übertragen.
    ::
    
        ipc = SharedMemoryIPC()
        walk = WalkingEngine()
        walk.x_move_amplitude = 10
        walk.start()
        while True:
            # Bewegung berechnen!
            walk.process()
            
            # Pose setzen
            ipc.set_pose(walk.pose)
            sleep(0.008)
        
    
    
    .. method:: start
        
        Startet den Laufvorgang. Ist :attr:`x_move_amplitude` und co
        auf Null gesetzt, so stampft der Roboter auf der Stelle herum.
    
    
    .. method:: stop
        
        Bringt den Roboter zum stehen.
    
    
    .. method:: process
        
        Muss alle acht Millisekunden aufgerufen werden und berechnet eine
        neue :class:`~pypose.PyPose`, die über :attr:`pose` ausgelesen
        werden kann.
    
    
    .. attribute:: pose
        
        Instanz von :class:`~pypose.PyPose` mit den aktuellen Zielwinkeln
        der Gelenke.
    
    
    .. attribute:: x_move_amplitude
        
        Ungefähre Geschwindigkeit nach vorne in Zentimetern pro Sekunde.
        
    
    .. attribute:: y_move_amplitude
        
        Ungefähre Geschwindigkeit zur Seite in Zentimetern pro Sekunde.
        
    
    .. attribute:: a_move_amplitude
        
        Ungefähre Drehgeschwindigkeit in Grad pro Sekunde.

    .. attribute:: parameters

       Gibt sämtliche Parameter zurück. Also: x, y, z, a, r, p, hip_pitch, pelvis
        def __get__(self): return Parameters(self)
    
