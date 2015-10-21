# -*- coding:utf-8 -*-
"""
Helper
^^^^^^

This is a helper class for some functions used in the behaviour

History:
* 05.12.14: Created (Marc Bestmann & Nils Rokita)
"""
import time


def become_one_time_kicker(connector):
    connector.blackboard_capsule().set_one_time_kicked(False)
    connector.blackboard_capsule().set_one_time_kicker_timer(time.time())
    connector.set_duty("OneTimeKicker")