#-*- coding:utf-8 -*-

#from bitbots.modules.basic.LocatorModule import LocatorModule
from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME
from bitbots.vision.robotvision import LinePoints
from bitbots.util.test.testUtils import get_init_pose

"""
    @Robert 29.04.2014: Currently disabled; Locator is not build regulary
"""

#class TestVisionModule(unittest.TestCase):
class TestLocatorModule(object):


    @classmethod
    def setUpClass(cls):
        print "#### Test LocatorModule ####"

    def prepare_data(self, locatorToggle = True, x_move = 0,
            y_move = 0, move_dir = 0, updated = False,
            new_frame = True, lp = None):
        data = {}
        config = {}
        toggel = {"Location": locatorToggle}
        config["Toggels"] = toggel
        config["vision"] = {}
        config["vision"]["CameraAngle"] = 86
        data["Config"] = config
        data["Moving.X"] = x_move
        data["Moving.Y"] = y_move
        data["Moving.Direction"] = move_dir
        data["transformerUpdated"] = updated
        data["CameraPose"] = get_init_pose()
        data[DATA_KEY_IS_NEW_FRAME] = new_frame
        data["Ipc"] = None
        if lp is not None:
            data["LinePoints"] = lp
        return data

    def get_minimal_line_points(self):
        return LinePoints()

    def setUp(self):
        self.lm = LocatorModule()

    def test_feature_toggle_enabled(self):
        return "Test Disabled, due to removing Locator from build @Robert 22.04.2014"
        data = self.prepare_data(locatorToggle = True,
            lp = self.get_minimal_line_points())
        self.lm.start(data)
        self.lm.update(data)
        self.assertTrue("Position" in data.keys())

    def test_feature_toggle_disabled(self):
        return "Test Disabled, due to removing Locator from build @Robert 22.04.2014"
        data = self.prepare_data(locatorToggle = False,
            lp = self.get_minimal_line_points())
        self.lm.update(data)
        self.assertFalse("Position" in data.keys())
        self.lm.start(data)
        self.lm.update(data)
        self.assertFalse("Position" in data.keys())
