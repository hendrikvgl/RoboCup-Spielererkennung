from bitbots.modules.abstract.stack_machine_module import StackMachineModule
from bitbots.modules.behaviour.head.decisions.head_duty_decider import HeadDutyDecider


class HeadModule(StackMachineModule):

    def __init__(self):
        self.set_start_module(HeadDutyDecider)


def register(ms):
    ms.add(HeadModule, "HeadModule",
           requires=["Ipc"],
           provides=[""])
