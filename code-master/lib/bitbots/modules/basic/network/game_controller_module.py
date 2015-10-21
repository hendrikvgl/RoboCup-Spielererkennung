# -*- coding:utf-8 -*-
"""
GameControllerModule
^^^^^^^^^^^^^^^^^^^^

Gets the data from the Gamecontroller via network and provides them in the data dictonary

History:
''''''''

* 01.04.12: Created (Nils Rokita)

* 08.01.14: Extansion for events (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)
"""
import time

from bitbots.modules.abstract import AbstractThreadModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.events import EVENT_PENALTY, EVENT_NO_PENALTY
from bitbots.modules.events import EVENT_GAME_STATUS_CHANGED
from bitbots.modules.events import EVENT_MANUAL_PENALTY, EVENT_GOAL
from bitbots.modules.events import EVENT_NO_MANUAL_PENALTY
from bitbots.game.receiver import GameStateReceiver
from bitbots.util import get_config
from bitbots.util.speaker import say

from bitbots.modules.keys import DATA_KEY_PENALTY, DATA_KEY_CONFIG, DATA_KEY_OWN_KICK_OF, DATA_VALUE_STATE_PLAYING, \
    DATA_KEY_GAME_STATUS, DATA_KEY_OWN_GOALS, DATA_KEY_ENEMY_GOALS, DATA_KEY_SECONDS_REMAINING, \
    DATA_KEY_SECONDAR_SECONDS_REMAINING, DATA_KEY_DROP_IN_TIME, DATA_VALUE_STATE_SET, DATA_VALUE_STATE_READY, \
    DATA_VALUE_STATE_INITIAL, DATA_KEY_KICK_OFF_TIME, DATA_KEY_DROP_BALL_TIME

config = get_config()


class GameControllerModule(AbstractThreadModule):
    """
    This module runs as a thread. At each circle all the data from the Gamecontoller is updated.
    """

    def __init__(self):
        super(GameControllerModule, self).__init__(
            requires=[DATA_KEY_CONFIG],
            provides=[DATA_KEY_GAME_STATUS, DATA_KEY_PENALTY,
                      DATA_KEY_OWN_KICK_OF, DATA_KEY_DROP_IN_TIME,
                      DATA_KEY_SECONDS_REMAINING, DATA_KEY_SECONDAR_SECONDS_REMAINING]
        )

        self.team = config["TEAM"]
        self.player = config["PLAYER"]
        self.address = config["ADDRESS"]

        self.set(DATA_KEY_GAME_STATUS, DATA_VALUE_STATE_PLAYING)
        self.set(DATA_KEY_PENALTY, False)
        self.set(DATA_KEY_OWN_KICK_OF, False)
        self.set(DATA_KEY_SECONDAR_SECONDS_REMAINING, -1)
        self.set(DATA_KEY_SECONDS_REMAINING, 999999)
        self.set(DATA_KEY_SECONDS_REMAINING, -1)

    def run(self):
        reciver = GameStateReceiver(team=self.team, player=self.player,
                                    addr=(self.address[0], self.address[1]))

        debug_m(2, "Teamnumber", str(self.team))
        debug_m(2, "Playernumber: " + str(self.player))
        debug_m(2, "Playernumber", str(self.player))

        # Manual penalty events will be passed to the receiver
        # to give it the ability to pass it to the Gamecontroller
        # There is no problem if the ManualPenaltyModule is not loaded, it just happens nothing
        self.register_to_event(
            EVENT_MANUAL_PENALTY,
            lambda data: reciver.set_manual_penalty(True))
        self.register_to_event(
            EVENT_NO_MANUAL_PENALTY,
            lambda data: reciver.set_manual_penalty(False))

        old_game_state = None
        old_penalty_status = False
        old_own_goals = -1
        block_missed = True
        while True:
            reciver.receive_once()
            state = reciver.get_last_state()
            if state is not None:
                block_missed = False
                if state.teams[0].team_number == self.team or state.teams[1].team_number == self.team:

                    self.set(DATA_KEY_GAME_STATUS, state.game_state)
                    debug_m(2, DATA_KEY_GAME_STATUS, state.game_state)

                    self.set(DATA_KEY_SECONDS_REMAINING, state.seconds_remaining)
                    self.set(DATA_KEY_SECONDAR_SECONDS_REMAINING, state.secondar_seconds_remaining)
                    self.set(DATA_KEY_DROP_IN_TIME, state.drop_in_time)

                    if state.game_state != old_game_state:
                        debug_m(2, "Gamestate has Changed: %s --> %s" % (
                            str(old_game_state), str(state.game_state)))
                        if old_game_state in (DATA_VALUE_STATE_SET, DATA_VALUE_STATE_READY, DATA_VALUE_STATE_INITIAL) \
                                and state.game_state == DATA_VALUE_STATE_PLAYING:
                            if 0 < DATA_KEY_DROP_IN_TIME < 30:
                                self.set(DATA_KEY_DROP_BALL_TIME, time.time())
                            else:
                                self.set(DATA_KEY_KICK_OFF_TIME, time.time())
                        old_game_state = state.game_state
                        self.send_event(EVENT_GAME_STATUS_CHANGED, state.game_state)

                    i = 0
                    for team in state.teams:
                        if team.team_number == self.team:
                            self.set(DATA_KEY_OWN_GOALS, team.score)
                            penalty = team.players[self.player - 1].penalty
                            if old_penalty_status != penalty:
                                if penalty:
                                    self.send_event(EVENT_PENALTY)
                                    self.set(DATA_KEY_PENALTY, True)
                                    debug_m(2, "Penalize")
                                else:
                                    self.send_event(EVENT_NO_PENALTY)
                                    self.set(DATA_KEY_PENALTY, False)
                                    debug_m(2, "Unpenalize")
                                self.set(DATA_KEY_PENALTY, penalty != 0)
                            goals = team.score
                            if goals != old_own_goals:
                                if old_own_goals != -1:
                                    self.send_event(EVENT_GOAL, goals)
                                old_own_goals = goals

                            debug_m(2, DATA_KEY_PENALTY, team.players[
                                self.player - 1].penalty != 0)
                            old_penalty_status = penalty
                            self.set(DATA_KEY_OWN_KICK_OF, state.kick_of_team == i)
                            debug_m(2,
                                    DATA_KEY_OWN_KICK_OF, str(state.kick_of_team == i))
                        else:
                            self.set(DATA_KEY_ENEMY_GOALS, team.score)
                        i += 1

            else:
                if not block_missed and reciver.get_time_since_last() > 10:
                    block_missed = True
                    # nach 10 sekunden kein packet setzen wir einige dinge
                    say("Lost Gamecontroler, will Play now")

                    self.set(DATA_KEY_GAME_STATUS, DATA_VALUE_STATE_PLAYING)
                    self.send_event(EVENT_GAME_STATUS_CHANGED, DATA_VALUE_STATE_PLAYING)
                    debug_m(2, DATA_KEY_GAME_STATUS, "STATE_PLAYING (Contorller Lost)")
                    if DATA_VALUE_STATE_PLAYING != old_game_state:
                        debug_m(2, "Gamestate has Changed due to Controler loss: %s --> %s" % (
                            str(old_game_state), DATA_VALUE_STATE_PLAYING))
                        old_game_state = DATA_VALUE_STATE_PLAYING
                    if old_penalty_status:
                        old_penalty_status = False
                        self.send_event(EVENT_NO_PENALTY)
                        self.set(DATA_KEY_PENALTY, False)
                        debug_m(2, "Unpenalize")
                debug_m(2, DATA_KEY_GAME_STATUS, "GameStatus is None")


def register(ms):
    ms.add(GameControllerModule, "GameContoller",
           requires=[DATA_KEY_CONFIG],
           provides=[
               DATA_KEY_GAME_STATUS,
               DATA_KEY_PENALTY,
               DATA_KEY_OWN_KICK_OF,
               EVENT_GOAL,
               DATA_KEY_OWN_GOALS,
               DATA_KEY_ENEMY_GOALS,
               DATA_KEY_SECONDS_REMAINING,
               DATA_KEY_SECONDAR_SECONDS_REMAINING,
               DATA_KEY_DROP_IN_TIME])