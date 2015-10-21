# -*- coding:utf-8 -*-
"""
SearchAndConfirm
^^^^^^^^^^^^^^^^

Searches and confirms the goal or ball

History:

* 25.03.2015: Created (Martin Poppinga)

"""
import time
from bitbots.modules.abstract.abstract_decision_module import AbstractDecisionModule
from bitbots.modules.behaviour.head.actions.track_object import TrackBall, TrackGoal
from bitbots.modules.behaviour.head.decisions.search_for_object import SearchForBall, SearchForEnemyGoal
from bitbots.util import get_config


class AbstractSearchAndConfirm(AbstractDecisionModule):
    def __init__(self, _):
        super(AbstractSearchAndConfirm, self).__init__(_)
        self.set_confirmed = None
        self.get_started_confirm_time = None
        self.set_started_confirm_time = None
        self.unset_started_confirm_time = None
        self.object_seen = None
        self.object_last_seen = None
        self.fr = True

        config = get_config()
        self.fail_counter = 0
        self.confirm_time = config["Behaviour"]["Common"]["Search"]["confirmTime"]
        self.track_ball_lost_time = config["Behaviour"]["Common"]["Tracking"]["trackBallLost"]
        self.ball_fail_conter_max = config["Behaviour"]["Common"]["Tracking"]["ballFailCounterMax"]

    def perform(self, connector, reevaluate=False):

        if time.time() - self.get_started_confirm_time() > self.confirm_time and \
                self.get_started_confirm_time() != 0:
            self.set_confirmed()
            self.unset_started_confirm_time()
            self.debug("confirmed")
            return self.pop()

        if self.object_seen():
            if time.time() - self.get_started_confirm_time() > self.confirm_time:
                self.set_started_confirm_time()
                self.fail_counter = 0
            self.fail_counter -= 1
            return self.track()
        else:
            self.fail_counter += 2
            if self.fail_counter >= self.ball_fail_conter_max:
                self.unset_started_confirm_time()  # stop confirming, because ball was lost
            if time.time() - self.object_last_seen() < self.track_ball_lost_time:
                return self.track()
            else:
                return self.search()

    def track(self):
        pass

    def search(self):
        pass

    def get_reevaluate(self):
        return True


class SearchAndConfirmBall(AbstractSearchAndConfirm):

    def perform(self, connector, reevaluate=False):
        if self.fr:
            self.fr = False
            self.get_started_confirm_time = connector.blackboard_capsule().get_started_confirm_ball
            self.set_started_confirm_time = connector.blackboard_capsule().set_started_confirm_ball
            self.unset_started_confirm_time = connector.blackboard_capsule().unset_started_confirm_ball
            self.set_confirmed = connector.blackboard_capsule().set_confirmed_ball
            self.object_seen = connector.raw_vision_capsule().ball_seen
            self.object_last_seen = connector.raw_vision_capsule().ball_last_seen
        super(SearchAndConfirmBall, self).perform(connector, reevaluate)

    def track(self):
        return self.push(TrackBall)

    def search(self):
        return self.push(SearchForBall)


class SearchAndConfirmEnemyGoal(AbstractSearchAndConfirm):
    def perform(self, connector, reevaluate=False):
        if self.fr:
            self.fr = False
            self.get_started_confirm_time = connector.blackboard_capsule().get_started_confirm_goal
            self.set_started_confirm_time = connector.blackboard_capsule().set_started_confirm_goal
            self.unset_started_confirm_time = connector.blackboard_capsule().unset_started_confirm_goal
            self.set_confirmed = connector.blackboard_capsule().set_confirmed_goal
            self.object_seen = connector.raw_vision_capsule().any_goal_seen
            self.object_last_seen = connector.raw_vision_capsule().any_goalpost_last_seen
        super(SearchAndConfirmEnemyGoal, self).perform(connector, reevaluate)

    def track(self):
        return self.push(TrackGoal)

    def search(self):
        return self.push(SearchForEnemyGoal)