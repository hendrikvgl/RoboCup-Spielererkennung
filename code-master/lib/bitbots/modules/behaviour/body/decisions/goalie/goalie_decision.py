"""
GoalieDecision
^^^^^^^^^^^^^^

Start of goalie Behaviou. Decides ic the goalie has to go back to its own goal.

History:
* 05.12.14: Created (Marc Bestmann & Nils Rokita)
"""
from bitbots.modules.abstract.abstract_decision_module import AbstractDecisionModule
from bitbots.modules.behaviour.body.decisions.common.ball_seen import BallSeenGoalie
from bitbots.modules.behaviour.body.decisions.common.go_to_duty_position import GoToDutyPosition


class GoalieDecision(AbstractDecisionModule):

    def perform(self, connector, reevaluate=False):

        if connector.blackboard_capsule().get_goalie_out_of_goal():
            return self.push(GoToDutyPosition)

        return self.push(BallSeenGoalie)