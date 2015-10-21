# -*- coding:utf-8 -*-
"""
HeadDutyDecider
^^^^^^^^^^^^^^^

Entscheidet was der Kopf tun soll

History:

* 19.08.14: Created (Nils Rokita)

"""
import time

from bitbots.modules.abstract.abstract_decision_module import AbstractDecisionModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.behaviour.head.decisions.search_and_confirm import SearchAndConfirmBall, SearchAndConfirmEnemyGoal
from bitbots.modules.behaviour.head.decisions.continious_search import ContiniousSearch
from bitbots.util import get_config


class HeadDutyDecider(AbstractDecisionModule):
    def __init__(self, _):
        super(HeadDutyDecider, self).__init__()
        toggles = get_config()["Behaviour"]["Toggles"]["Head"]
        self.toggle_goal_vison_tracking = toggles["goalVisionTracking"]
        self.toggle_switch_ball_goal = toggles["switchBallGoalSearch"]
        config = get_config()
        self.confirm_time = config["Behaviour"]["Common"]["Search"]["confirmTime"]
        self.last_confirmd_goal = 0
        self.fail_goal_counter = 0
        self.ball_prio = 0
        self.goal_prio = 0
        self.trackjustball_aftergoal = False

    def perform(self, connector, reevaluate=False):
        # todo refactor in more decisions
        """ This is the root for the head stack machine """

        if connector.raw_vision_capsule().ball_seen():
            self.ball_prio = max(0, self.ball_prio - 3)
        else:
            self.ball_prio = min(120, self.ball_prio + 5)

        if connector.raw_vision_capsule().any_goal_seen():
            self.goal_prio = max(0, self.goal_prio - 2)
        else:
            self.goal_prio = min(100, self.goal_prio + 3)

        debug_m(4, "GoalPrio", self.goal_prio)
        debug_m(4, "BallPrio", self.ball_prio)
        debug_m(4, "BallLastCOnfirmed", time.time() - connector.blackboard_capsule().get_confirmed_ball())
        debug_m(4, "BallLastStratedconfirm", time.time() - connector.blackboard_capsule().get_started_confirm_ball())

        if connector.blackboard_capsule().is_no_head_movement_at_all():
            debug_m(4, "Headdoes", "Nothing")
            return self.interrupt()

        if connector.blackboard_capsule().is_ball_tracking_still_active():
            debug_m(4, "Headdoes", "BallTracking")
            return self.push(SearchAndConfirmBall)

        if connector.blackboard_capsule().is_enemy_goal_tracking_still_active():
            debug_m(4, "Headdoes", "GoalTracking")
            return self.push(SearchAndConfirmEnemyGoal)

        if connector.blackboard_capsule().is_tracking_both_still_active():  # todo to be tested
            debug_m(4, "TrackbothTime", time.time())
            if time.time() - connector.blackboard_capsule().get_confirmed_ball() > 5:
                debug_m(4, "Headdoes", "TrackBothBall")
                return self.push(SearchAndConfirmBall)

            # ball long enough seen
            elif time.time() - connector.blackboard_capsule().get_confirmed_goal() > 6:
                debug_m(4, "Headdoes", "TrackBothGoal")
                return self.push(SearchAndConfirmEnemyGoal)

            elif self.trackjustball_aftergoal:
                debug_m(4, "Headdoes", "TrackBothElse")
                return self.push(SearchAndConfirmBall)

        if self.toggle_switch_ball_goal:
            debug_m(4, "Headdoes", "Priorities")
            if self.ball_prio >= self.goal_prio:
                return self.push(SearchAndConfirmBall)
            else:
                return self.push(SearchAndConfirmEnemyGoal)

        # Default Head Behaviour
        debug_m(4, "Headdoes", "Standardsearch")
        return self.push(ContiniousSearch)

    def get_reevaluate(self):
        return True
