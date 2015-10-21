# -*- coding:utf-8 -*-
"""
PlainWalkAction
^^^^^^^^^^^^^^^

.. moduleauthor:: Sheepy

History:
* Created (Sheepy)

The robot performs a cretain set of walking parameters. The action expects a list of 4-tuples as first argument.

"""
import time

from bitbots.modules.abstract.abstract_init_action_module import AbstractInitActionModule


class PlainWalkAction(AbstractInitActionModule):
    def __init__(self, args):
        AbstractInitActionModule.__init__(self, args)
        self.step_list = args
        self.walking_steps = self.walking_step_generator_function()
        self.active = False

    def walking_step_generator_function(self):
        """ This is a coroutine for head movement """
        if self.step_list is None:
            raise Exception("Step list may not be None.")
        for element in self.step_list:
            yield element
        yield None

    def perform(self, connector, reevaluate=False):
        if connector.get_duty() in ["ThrowIn", "PenaltyKickFieldie"]:
            self.do_not_reevaluate()
        if not self.active:
            self.current_step = self.walking_steps.next()
            if self.current_step is None:
                connector.walking_capsule().stop_walking()
                return self.pop()
            f, a, s, t = self.current_step
            self.active = True
            self.started_time = time.time()

            connector.walking_capsule().start_walking(f, a, s)
        else:
            if time.time() > self.current_step[3] + self.started_time:
                self.active = False
