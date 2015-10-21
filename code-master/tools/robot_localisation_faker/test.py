import threading
import time
from bitbots.modules.basic.network.game_controller_module import GameControllerModule
from bitbots.modules.basic.worldmodel.localization_module import LocalizationModule

__author__ = 'sheepy'


data = {}

class DummySurrounder(threading.Thread):

    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data
        self.lm = GameControllerModule()
        self.lm.start(self.data)

    def run(self):
        while True:
            self.lm.update(self.data)


ds = DummySurrounder(data)
ds.start()


while True:
    print "Data", data
    time.sleep(1)