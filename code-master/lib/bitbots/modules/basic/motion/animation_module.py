#-*- coding:utf-8 -*-
"""
AnimationModule
^^^^^^^^^^^^^^^

Module for playing animations

History:
''''''''

* ??.??.11 Created (Olli Bestmann)

* ??.??.12 Completly changed (Nils Rokita)

* 05.08.14 Refactor (Marc Bestmann)
"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m

from bitbots.util.animation import play_animation

from bitbots.ipc import STATE_WALKING

from bitbots.modules.keys import DATA_KEY_IPC, DATA_KEY_ANIMATION, DATA_KEY_WALKING_ACTIVE, DATA_KEY_WALKING_RUNNING


class AnimationModule(AbstractModule):
    """
    This modules takes a animation, which should be played, from data['Animation'] and plays it.
    The module takes care to just play one animation at a time by just taking the next animation if there is no
     animation played currently.

    .. Warning::
        This means that while a aniamtion is played (or :mod:`bitbots.ipc.ipc.SharedMemoryIPC` because of other things
        on state not controlable is)
        Animationswünsche einfach ignoriert werden.

    Also it is necessary to take care of stopping the walking to play animations.
    """
    def __init__(self):
        self.next = None

    def post(self, data):
        """
        This module does its work in :func:`post` to directly play anitmaitons which were provided in this cycle.
        """
        ipc = data[DATA_KEY_IPC]
        if self.next is None and data.get(DATA_KEY_ANIMATION, None) is not None:
            # Animation merken
            self.next = data[DATA_KEY_ANIMATION]
            debug_m(2, "Next", str(self.next))
            data[DATA_KEY_ANIMATION] = None

        if self.next is None:
            # Wir haben bisher keine Animation
            return

        if (not ipc.controlable) and ipc.get_motion_state() != STATE_WALKING:
            # Wenn wir im state Walking sind müssen wir einfach noch etwas
            # Warten, das stoppen wir dann gleich.
            debug_m(1, "Could not start Annimation %s." %
                str(self.next) + "Ipc is in state %s" % ipc.get_motion_state())
            # Wir haben keine Kontrolle oder spielen schon was,
            # ignoriere die aktuelle Animation
            if isinstance(self.next, (tuple, list)):
                # callback mit fail aufruffen
                self.next[1](False)
            self.next = None
            return

        # Walking jetzt stoppen
        data[DATA_KEY_WALKING_ACTIVE] = False

        # Wenn Walking nicht mehr läuft, Animation starten
        if self.next is not None and \
                not data.get(DATA_KEY_WALKING_RUNNING, False):
            # debug.log("Animation abspielen")
            if isinstance(self.next, (tuple, list)):
                # da ist ein callback dabei
                if not play_animation(self.next[0], ipc, self.next[1]):
                    # schon beim starten gescheitert, wir ruffen das callback
                    # mit False auf
                    self.next[1](False)
            else:
                #ohne callback
                play_animation(self.next, ipc)
            self.next = None
            debug_m(2, "Next", str(self.next))
        elif data.get(DATA_KEY_WALKING_RUNNING, False):
            debug_m(2, "Wait for stopping of the walking")


def register(ms):
    ms.add(AnimationModule, "AnimationModule",
           requires=[DATA_KEY_IPC,
                     DATA_KEY_WALKING_ACTIVE,
                     DATA_KEY_WALKING_RUNNING],
           provides=[])
