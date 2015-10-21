# -*- coding:utf-8 -*-
"""
DebugLevel
^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 03.12.14: Created (sheepy)

"""

class DebugLevel():

    # This field includes debug that is necessary such that the debug-ui get the necessary information to view
    # what the robots believes during the game.
    # (that includes in general such things as ball found, goal found, position, critical error)
    DURING_GAME_DEBUG = 1

    # This includes debug that is send during game preparation - it includes much more fine granular debug that could
    # be for example the exact uv values and angles and other stuff that is necessary to investigate a problem with
    # configuration more in depth
    GAME_PREPARE_DEBUG = 2

    COME_UP_WITH_CATEGORY_DEBUG = 3

    LEVEL_4 = 4

    # This are messages that can be used during development or just getting feedback from the robot which is absolutely
    # not necessary for other things
    CUSTOM_DEBUG = 5

