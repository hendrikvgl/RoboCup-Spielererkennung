# This comes from bitbots.modules.basic.__init__.py
from bitbots.modules.basic import get_enabled_basic_modules

BASIC_IMPORTS = get_enabled_basic_modules()

##############################################
### Start UP Information for new Behaviour ###
##############################################
BEHAVIOUR_IMPORTS = BASIC_IMPORTS + ["bitbots.modules.behaviour.behaviour"] + ["bitbots.modules.behaviour.head.head_module"]
BEHAVIOUR_RUNS = [
    "BehaviourModule",
    "HeadModule",
    "Speaker",
    "Penalizer",
    "AnimationModule",
    "Walking",
    "StandUp",
    "ManuelStart",
    "Torjubel",
    "ResetWorldModel",
]

##############################################
### Start UP Information for new  TestBehaviour ###
##############################################
TESTBEHAVIOUR_IMPORTS = BASIC_IMPORTS + ["bitbots.modules.behaviour.test_behaviour"] + ["bitbots.modules.behaviour.head.head_module"]
TESTBEHAVIOUR_RUNS = [
    "TestBehaviourModule",
    "HeadModule",
    "Speaker",
    "Penalizer",
    "AnimationModule",
    "Walking",
    "StandUp",
    "ResetWorldModel",
]

#####################################
### Start UP Information for Demo ###
#####################################
DEMO_RUNS = [
        "NetworkController",
        "ButtonController",
        "AnimationModule"
]


VISUALIZATION_RUNS = [
    "Visualization",
    "BallVisualization",
    "GoalVisualization",
    "LegendWindow"
]