import unittest
import math
from Robot import Robot
from WorldService import WorldService


class TestWorldService(unittest.TestCase):

    worldService = WorldService()

    def test_walking_simple_forward(self):
        r = Robot("Tamara", [0, 0], 0)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 1
        r.sideward = 0
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(1, r.xy[0])
        self.assertAlmostEqual(0, r.xy[1])

    def test_walking_simple_backward(self):
        r = Robot("Tamara", [0, 0], 0)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = -1
        r.sideward = 0
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(-1, r.xy[0])
        self.assertAlmostEqual(0, r.xy[1])

    def test_walking_simple_sidewards_left(self):
        r = Robot("Tamara", [0, 0], 0)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = -1
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(0, r.xy[0])
        self.assertAlmostEqual(1, r.xy[1])

    def test_walking_simple_sidewards_right(self):
        r = Robot("Tamara", [0, 0], 0)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 1
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(0, r.xy[0])
        self.assertAlmostEqual(-1, r.xy[1])


    def test_walking_simple_sidewards_left_angle(self):
        r = Robot("Tamara", [0, 0], 90)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = -1
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(-1, r.xy[0])
        self.assertAlmostEqual(0, r.xy[1])

    def test_walking_simple_sidewards_right_angle(self):
        r = Robot("Tamara", [0, 0], 90)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 1
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(1, r.xy[0])
        self.assertAlmostEqual(0, r.xy[1])

    def test_walking_simple_axis_left(self):
        r = Robot("Tamara", [0, 0], 180)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 1
        r.sideward = 0
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(-1, r.xy[0])
        self.assertAlmostEqual(0, r.xy[1])


    def test_walking_simple_axis_up(self):
        r = Robot("Tamara", [0, 0], 90)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 1
        r.sideward = 0
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(0, r.xy[0])
        self.assertAlmostEqual(1, r.xy[1])


    def test_walking_simple_axis_down(self):
        r = Robot("Tamara", [0, 0], 270)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 1
        r.sideward = 0
        r.angular = 0
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(0, r.xy[0])
        self.assertAlmostEqual(-1, r.xy[1])


    def test_walking_angular_turn(self):
        r = Robot("Tamara", [0, 0], 0)
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 0
        r.angular = 10
        self.worldService.update_robot(r, 1)

        self.assertAlmostEqual(10, r.orientation)


    def test_ball_relative_position(self):
        self.worldService.register_robot("Tamara")

        r = self.worldService.robots["Tamara"]
        r.orientation = 0
        r.xy = [-400, 0]
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 0
        r.angular = 0

        self.worldService.ball = [0, 0, 0, 0]

        u, v, distance = self.worldService.get_update_info("Tamara")

        self.assertAlmostEqual(400, distance)
        self.assertAlmostEqual(400, u)
        self.assertAlmostEqual(0, v)


    def test_ball_relative_position_second(self):
        self.worldService.register_robot("Tamara")

        r = self.worldService.robots["Tamara"]
        r.orientation = 0
        r.xy = [-400, -400]
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 0
        r.angular = 0

        self.worldService.ball = [0, 0, 0, 0]

        u, v, distance = self.worldService.get_update_info("Tamara")

        self.assertAlmostEqual(math.sqrt(400**2+400**2), distance)
        self.assertAlmostEqual(400, u)
        self.assertAlmostEqual(400, v)


    def test_ball_relative_position_third(self):
        self.worldService.register_robot("Tamara")

        r = self.worldService.robots["Tamara"]
        r.orientation = 135
        r.xy = [-400, -400]
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 0
        r.angular = 0

        self.worldService.ball = [0, 0, 0, 0]

        u, v, distance = self.worldService.get_update_info("Tamara")

        self.assertAlmostEqual(math.sqrt(400**2+400**2), distance)
        self.assertAlmostEqual(0, u)
        self.assertAlmostEqual(math.sqrt(400**2+400**2), v)


    def test_ball_relative_position_third(self):
        self.worldService.register_robot("Tamara")

        r = self.worldService.robots["Tamara"]
        r.orientation = -45
        r.xy = [-400, -400]
        r.forward_multiplicator = 1
        r.sideward_multiplicator = 1
        r.angular_multiplicator = 1
        r.forward = 0
        r.sideward = 0
        r.angular = 0

        self.worldService.ball = [0, 0, 0, 0]

        u, v, distance = self.worldService.get_update_info("Tamara")

        self.assertAlmostEqual(math.sqrt(400**2+400**2), distance)
        self.assertAlmostEqual(0, u)
        self.assertAlmostEqual(math.sqrt(400**2+400**2), v)


