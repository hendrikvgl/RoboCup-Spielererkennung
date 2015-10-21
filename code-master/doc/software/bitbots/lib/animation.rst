Animation
=========

.. automodule:: bitbots.motion.animation

Repräsentation
--------------

JSON-Datei
""""""""""
Die Animationen werden im JSON-Datenformat gespeichert, und bei bedraf eingelesen.

Werte:
++++++

.. object:: name

  Anzeigename dieser Animation. Meist Identisch mit dem Dateinamen.

  :type: String

.. object:: description

  Aussagekräftige Beschreibung der Animation.
  Sollte im rst-Format geschrieben werden auch wenn wir derzeit noch nix daraus generieren.

  :type: String

.. object:: hands

  Parameter der der die compabilität der animation für Roboter mit Händen angibt.
  Default-Wert ist "Ignore"

  :type: String
  :key Yes: Hände sind *zwingend* erforderlich
  :key No: Hände sind *verboten*
  :key Ignore: Hände sind egal **(default)**

.. object:: default_interpolator

  Interpolator to use when no other one is specified for a Keyframe.

  :type: String
  :key LinearInterpolator: .. todo:: docme
  :key CatMulInterpolator: .. todo:: docme

.. object:: keyframes

  Eine Liste aller Keyframes dieser Animation

  :type: List

  .. describe:: Keyframe

    Ein Keyframe als element der Keyframeliste.
    Ein Key wird in der Liste nicht angegeben, lediglich
    die {} um einen Keyframe als Dictionary abzugrenzen.

    .. object:: duration

      Angestrebte Dauer des Keyframes in Sekunden.
      Die angeforderte Zeit kann nicht garantiert werden.

      :type: Float

    .. object:: pause

      Wartezeit *nach* dem Erreichen des Keyframes, bis mit dem
      anfahren des nächsten Keyframes begonnen wird.

      :type: Float

    .. object:: p

      Dictonary mit den P-Gains für die Motoren in diesem Keyframe.
      Wird ein Motor nicht spezifiziert, so bleibt er auf dem vorherigen
      wert. der P-Gain wird nur für Motoren gesetzt die in diesem
      Keyframe auch ein goal haben. (hat interne gründe).
      Kleine werte machen den Motor "weicher" höhere werte lassen ihn sehr
      schnell und stark reagieren,reagiert dann aber auch über

      .. warning::
        Wenn keine pause und oder duration angegeben ist kann es zu internen
        fehlern kommen

      .. warning::
        Die werte werden am ende nicht zurückgesetzt, man sollte sehr es
        im letzten frame tun

    .. object:: goals

      Dictionary mit den Zielwinkeln für die Motoren in diesem Keyframe.
      Wird ein Motor nicht spezifiziert, so wird er ignoriert und bleibt
      auf seiner Position. Das ist *kein* fehler, sondern mitunter notwendig.
      (z.B. laufen und dabei etwas in den Händen halten)

      :type: Dictionary

      .. object:: RShoulderPitch

        :var id: 1
        :var tags: Arms, RArm
        :var min: 0
        :var max: 4096

      .. object:: LShoulderPitch

        :var id: 2
        :var tags: Arms, LArm
        :var min: 0
        :var max: 4096

      .. object:: RShoulderRoll

        :var id: 3
        :var tags: Arms, RArm
        :var min:
        :var max:

      .. object:: LShoulderRoll

        :var id: 4
        :var tags: Arms, LArm
        :var min: 0
        :var max: 4096

      .. object:: RElbow

        :var id: 5
        :var tags: Arms, RArm
        :var min: 0
        :var max: 4096

      .. object:: LElbow

        :var id: 6
        :var tags: Arms, LArm
        :var min: 0
        :var max: 4096

      .. object:: RHipYaw

        :var id: 7
        :var tags: Legs, RLeg, RHip, Hips
        :var min: 0
        :var max: 4096

      .. object:: LHipYaw

        :var id: 8
        :var tags: Legs, LLeg, LHip, Hips
        :var min: 0
        :var max: 4096

      .. object:: RHipRoll

        :var id: 9
        :var tags: Legs, RLeg, RHip, Hips
        :var min: 0
        :var max: 4096

      .. object:: RHipRoll

        :var id: 10
        :var tags: Legs, LLeg, LHip, Hips
        :var min: 0
        :var max: 4096

      .. object:: RHipPitch

        :var id: 11
        :var tags: Legs, RLeg, RHip, Hips
        :var min: 0
        :var max: 4096

      .. object:: LHipPitch

        :var id: 12
        :var tags: Legs, LLeg, LHip, Hips
        :var min: 0
        :var max: 4096

      .. object:: RKnee

        :var id: 13
        :var tags: Legs, RLeg, Knees
        :var min: 0
        :var max: 4096

      .. object:: LKnee

        :var id: 14
        :var tags: Legs, LLeg, Knees
        :var min: 0
        :var max: 4096

      .. object:: RAnklePitch

        :var id: 15
        :var tags: Legs, RLeg, RFoot, AnklePitch, Feet
        :var min: 0
        :var max: 4096

      .. object:: LAnklePitch

        :var id: 16
        :var tags: Legs, LLeg, LFoot, AnklePitch, Feet
        :var min: 0
        :var max: 4096

      .. object:: RAnkleRoll

        :var id: 17
        :var tags: Legs, RLeg, RFoot, AnkleRoll, Feet
        :var min: 0
        :var max: 4096

      .. object:: LAnkleRoll

        :var id: 18
        :var tags: Legs, LLeg, LFoot, AnkleRoll, Feet
        :var min: 0
        :var max: 4096

      .. object:: HeadPan

        :var id: 19
        :var tags: Head
        :var min: 0
        :var max: 4096

      .. object:: HeadTilt

        :var id: 19
        :var tags: Head
        :var min: 0
        :var max: 4096

      .. object:: RElbowRoll

        (Nur Roboter mit Händen)

        :var id: 21
        :var tags: Arms, RArm, Elbows, RElbow
        :var min: 0
        :var max: 4096

      .. object:: LElbowRoll

        (Nur Roboter mit Händen)

        :var id: 22
        :var tags: Arms, LArm, Elbows, LElbow
        :var min: 0
        :var max: 4096

      .. object:: RHand

        (Nur Roboter mit Händen)

        :var id: 23
        :var tags: Hands, Arms, RArm
        :var min: 0
        :var max: 4096

      .. object:: LHand

        (Nur Roboter mit Händen)

        :var id: 24
        :var tags: Hands, Arms, LArm
        :var min: 0
        :var max: 4096

Beispiel
++++++++
.. code-block:: javascript

  {
      "default_interpolator": "LinearInterpolator",
      "name": "example",
      "hands": "ignore",
      "description": "Simple Description Text",

      "keyframes": [
          {
              "duration": 0.496,
              "pause": 0.0,
              "goals": {
                  "LShoulderPitch": 41.30859375,
                  "LShoulderRoll": 17.578125,
                  "RShoulderRoll": -17.841796875,
                  "LKnee": -53.173828125,
                  "RHipYaw": 0.0,
                  "LAnklePitch": -29.970703125,
                  "RKnee": 53.173828125,
                  "RAnkleRoll": 0.791015625,
                  "RAnklePitch": 29.970703125,
                  "LHipPitch": 36.123046875,
                  "LHipYaw": 0.0,
                  "LHipRoll": -0.3515625,
                  "RHipRoll": 0.3515625,
                  "LAnkleRoll": -0.791015625,
                  "LElbow": -29.53125,
                  "RElbow": 29.267578125,
                  "RHipPitch": -36.123046875,
                  "RShoulderPitch": -48.33984375
              },
              "p": {
                  "LKnee": 68,
                  "RKnee": 68
              }
          }
      ]
  }

Python-Object
"""""""""""""
.. autoclass:: Animation(keyframes)

    .. attribute:: keyframes

        Eine Liste von :class:`Keyframe`-Objekten,
        die nacheinander abgefahren werden

    .. attribute:: interpolators

        Eine Zuordnung von Gelenknamen auf Klassen, die von
        :class:`Interpolator` erben

    .. attribute:: default_interpolator

        Die :class:`Interpolator`-Klasse, die für Gelenke genutzt wird,
        die nicht in :attr:`interpolators` umdefiniert sind

    .. automethod:: get_interpolator(name)

    .. automethod:: get_steps(name)

.. autoclass:: Keyframe(goals, time=1, pause=0, p={})


.. autofunction:: parse(info)


.. autofunction:: as_dict(animation)



Interpolation von Stützwerten
-----------------------------

.. autoclass:: Interpolator
    :members: prepare

    .. automethod:: interpolate(t)


    .. attribute:: steps

        Liste der Stützstellen (als :class:`Step` Objekte)


.. autoclass:: LinearInterpolator


.. autoclass:: CubicHermiteInterpolator


.. autoclass:: CatmullRomInterpolator


.. autoclass:: Step(time, value)

    .. attribute:: time

        Zeitwert der Stützstelle


    .. attribute:: value

        Wert an dem Zeitpunkt der Stützstelle


Abspielen einer Animation
-------------------------

.. autoclass:: Animator(animation, first_pose=None)

    .. automethod:: get_pose(t, pose=None)

    .. automethod:: play(ipc, stepsize=0.05)

Beispiel
""""""""

Das Abspielen einer Animation geschieht mit der :class:`Animator` Klasse.
Dazu muss die :class:`Animation` über :func:`parse` gelasden werden::

    with open("animation.json") as fp:
        anim = Animation(parse(json.load(fp)))

    Animator(anim).play(ipc, ipc.get_pose())

