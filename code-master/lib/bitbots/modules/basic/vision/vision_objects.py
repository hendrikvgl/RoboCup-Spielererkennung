from collections import namedtuple
from bitbots.modules.keys import DATA_KEY_GOAL_INFO

# U is Distance in Front # V the Distance Left
BallInfo = namedtuple("BallInfo", ("u", "v", "x", "y", "radius", "rating", "distance"))
GoalInfo = namedtuple(DATA_KEY_GOAL_INFO, ("x", "y", "u", "v", "width", "height"))
ObstacleInfo = namedtuple("ObstacleInfo", ("u", "v", "x", "y", "h", "w", "color"))

