from multiprocessing import Queue
import time
import pygame
import socket
import threading
import math
from bitbots.modules.basic.worldmodel.localization_module import PositionSettingPackage, KeepAliveRobotPackage

WINDOWWIDTH = 900+70*2
WINDOWHEIGHT = 600+70*2
CPS = 100

ZERO_X = 450 + 70
ZERO_Y = 300 + 70


TARGET_IP_ROBOTS = "192.168.108.11"
ROBOT_BASE_PORT = 9050


class ShallowRobot():

    def __init__(self, robot_id, port):
        self.robot_id = robot_id
        self.last_time_tried_ack = 0
        self.last_ack_time = 0
        self.current_px = 0
        self.current_py = 0
        self.current_orientation = 0
        self.changed = False
        self.conn_data = (TARGET_IP_ROBOTS, ROBOT_BASE_PORT+port)
        self.robot_says_x = 10
        self.robot_says_y = 10
        self.robot_says_orientation = 0
        self.last_time_send_position_update = 0

    def retry_time_up(self):
        if time.time() - self.last_time_tried_ack > 1:
            self.last_time_tried_ack = time.time()
            return True
        return False

    def set_updated_position(self, mx, my):
        if mx != self.current_px or my != self.current_py:
            self.current_px = mx
            self.current_py = my
            self.changed = True

    def update_orientation(self, delta):
        self.current_orientation += delta
        self.changed = True

    def test_and_reset_has_changed(self):
        # make sure we send only all 500ms
        if time.time() - self.last_time_send_position_update < 1:
            return False
        else:
            self.last_time_send_position_update = time.time()
            g = self.changed
            self.changed = False
            return g

    def is_active(self):
        # a robot is active when we heard from him in the last 5 seconds
        return time.time() - self.last_ack_time < 5

    def get_conn_data(self):
        return self.conn_data

    def update_ack_time(self):
        self.last_ack_time = time.time()

    def set_position_the_robot_told_us(self, x, y, orientation):
        self.robot_says_x = x
        self.robot_says_y = y
        self.robot_says_orientation = orientation

    def get_local_position(self):
        return self.current_px, self.current_py, self.current_orientation

    def get_robot_thinks_position(self):
        return self.robot_says_x, self.robot_says_y, self.robot_says_orientation


class RobotPositionLogic(object):

    def __init__(self):

        self.currently_active_robot = None

        self.all_robots_list = [
            ShallowRobot(1, 1),
            ShallowRobot(2, 2),
            ShallowRobot(3, 3),
            ShallowRobot(4, 4),
            ShallowRobot(99, 99)
        ]

        self.id_map = {s.robot_id: s for s in self.all_robots_list}

    def set_currently_active_robot(self, index):
        self.currently_active_robot = self.all_robots_list[index]

    def process_mouse_events(self, events):
        pass

    def process_ack_package(self, player, x, y, orientation, direction):
        if player in self.id_map:
            robot = self.id_map[player]
            robot.set_position_the_robot_told_us(x, y, orientation)
        else:
            print "[Error] got Package from Robot i don't know: ", player

    def get_robots_not_active(self):
        pass

    def set_robot_acked(self, robot_player_id):
        if robot_player_id in self.id_map:
            self.id_map[robot_player_id].update_ack_time()


class ManualRobotPositionSetter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        pygame.init()

        self.udp_port = 55555
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.udp_port))

        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH+CPS, WINDOWHEIGHT), pygame.HWSURFACE)


        pygame.display.set_caption('ManualRobotPositionSetter')
        self.input_queue = Queue()

        self.robot_position_tracker = RobotPositionLogic()


        # Start the input thread for networking operations
        self.start()

        # Start the main game loop
        self.main_game_loop()

    def run(self):
        """ This method reads the information from the server and processes the packages """

        while True:
            data, addr = self.sock.recvfrom(1024)


            package_length = self.determine_package_length(data[0:2])
            package = data[2:package_length+2]

            command, info = package[0:3], package[3:package_length]
            print "Comm/Inf", command, info

            self.input_queue.put((command, info, addr))

    def main_game_loop(self):

        while True:

            # Clear GUI Area with Black Rect
            pygame.draw.rect(self.DISPLAYSURF, (0, 255, 0), pygame.Rect(0, 0, WINDOWWIDTH, WINDOWHEIGHT))

            pygame.draw.rect(self.DISPLAYSURF, (255, 255, 255), pygame.Rect(70, 70, WINDOWWIDTH-2*70, WINDOWHEIGHT-2*70), 5)
            pygame.draw.rect(self.DISPLAYSURF, (0, 255, 150), pygame.Rect(ZERO_X-100, ZERO_Y-30, 150, 60))

            pygame.draw.polygon(self.DISPLAYSURF, (0, 255, 150), [
                [ZERO_X+50, ZERO_Y-30], [ZERO_X+50, ZERO_Y-50],
                [ZERO_X+100, ZERO_Y], [ZERO_X+50, ZERO_Y+50]
            ])


            pygame.draw.circle(self.DISPLAYSURF, (255, 255, 255), (ZERO_X, ZERO_Y), 75, 5)
            pygame.draw.circle(self.DISPLAYSURF, (255, 255, 255), (ZERO_X, ZERO_Y), 6, 5)
            pygame.draw.line(self.DISPLAYSURF, (255, 255, 255), (ZERO_X, ZERO_Y-300), (ZERO_X, ZERO_Y+300), 5)



            # Get all the events that happened during the cycle and process them by the logic
            pygame.draw.rect(self.DISPLAYSURF, (255, 255, 255), pygame.Rect(ZERO_X -450, ZERO_Y - 345/2, 60, 345), 5)
            pygame.draw.rect(self.DISPLAYSURF, (255, 255, 255), pygame.Rect(ZERO_X + 450 - 60, ZERO_Y - 345/2, 60, 345), 5)

            events = pygame.event.get()

            filtered_events = [e for e in events if e.type in (pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP)]
            event_md = len([e for e in filtered_events if e.button == 5])
            event_mu = len([e for e in filtered_events if e.button == 4])

            delta = event_md - event_mu

            if self.robot_position_tracker.currently_active_robot is not None:
                self.robot_position_tracker.currently_active_robot.update_orientation(5*delta)

            # Check if the mouse is clicking inside a specific area to change the robot that is chosen
            mouse_position = pygame.mouse.get_pos()
            mouse_button_state = pygame.mouse.get_pressed()

            m1, m2, m3 = mouse_button_state
            mx, my = mouse_position

            if WINDOWWIDTH < mx < WINDOWWIDTH+CPS:
                # Handle the possible button presses to switch robot thingys
                if m1 == 1:
                    index = int(my / 100.0)
                    self.robot_position_tracker.set_currently_active_robot(index)
                    print "Active Robot assignment changed"

            if 0 < mx < WINDOWWIDTH and 0 < my < WINDOWHEIGHT:
                # Mouse is over the field so we need to update the current robot position if the mouse button is pressed
                if m1 == 1:
                    active_robot = self.robot_position_tracker.currently_active_robot
                    if active_robot is not None:
                        active_robot.set_updated_position(mx, my)
                    print "Active Robot position changed by gui"


                self.robot_position_tracker.process_mouse_events(events)

            while not self.input_queue.empty():
                element = self.input_queue.get()

                command, payload, addr = element
                if command == "POS":
                    psp = PositionSettingPackage.from_string(payload)
                    player, x, y, orientation, direction = psp
                    print "Got pos ack", x, y, orientation
                    x += ZERO_X
                    y += ZERO_Y
                    self.robot_position_tracker.process_ack_package(player, x, y, orientation, direction)

                if command == "KAL":
                    robot_player_id = int(addr[1]) - ROBOT_BASE_PORT
                    print "Want to set robot to acked", robot_player_id
                    self.robot_position_tracker.set_robot_acked(robot_player_id)


            counter = 0
            for robot in self.robot_position_tracker.all_robots_list:

                bg_colour = (0, 150, 0) if robot.is_active() else (255, 0, 0)
                pygame.draw.rect(self.DISPLAYSURF, bg_colour, pygame.Rect(WINDOWWIDTH, counter*CPS, CPS, CPS))

                name_tag_font = pygame.font.Font('freesansbold.ttf', 24)
                name_tag = name_tag_font.render(str(robot.robot_id), True, (0, 0, 0))
                name_tag_rect = name_tag.get_rect()
                name_tag_rect.center = (WINDOWWIDTH+ CPS/2, counter*CPS+50)
                self.DISPLAYSURF.blit(name_tag, name_tag_rect)

                if robot == self.robot_position_tracker.currently_active_robot:
                    pygame.draw.rect(self.DISPLAYSURF, (255, 255, 0), pygame.Rect(WINDOWWIDTH, counter*CPS, CPS, CPS), 2)
                else:
                    pygame.draw.rect(self.DISPLAYSURF, (0, 0, 0), pygame.Rect(WINDOWWIDTH, counter*CPS, CPS, CPS), 2)

                counter += 1

            for robot in self.robot_position_tracker.all_robots_list:

                # Wee need to check which robots have changed positions and update them
                if robot.test_and_reset_has_changed():
                    pass # TODO send update package to robot
                    x, y, orientation = robot.current_px, robot.current_py, robot.current_orientation
                    x -= ZERO_X
                    y -= ZERO_Y
                    package = PositionSettingPackage.build_package(robot.robot_id, x, y, orientation, 1)
                    self.send_message(self.sock, package, robot.get_conn_data())

                # Wee need to check for all robots each n time to check if they are actually there
                if robot.retry_time_up():
                    package = KeepAliveRobotPackage.build_package()
                    self.send_message(self.sock, package, robot.get_conn_data())
                    print "sendec KAL package ", robot.robot_id

                lx, ly, lo = robot.get_local_position()
                tx, ty = 15*math.cos(math.pi*2 *lo/360.0), 15*math.sin(math.pi*2 *lo/360.0)
                pygame.draw.line(self.DISPLAYSURF, (255, 125, 0), (lx, ly), (lx+tx, ly+ty), 2)
                pygame.draw.circle(self.DISPLAYSURF, (255, 125, 0), (lx, ly), 10)
                name_tag_font = pygame.font.Font('freesansbold.ttf', 12)
                name_tag = name_tag_font.render(str(robot.robot_id), True, (0, 0, 0))
                name_tag_rect = name_tag.get_rect()
                name_tag_rect.center = (lx, ly)
                self.DISPLAYSURF.blit(name_tag, name_tag_rect)

                # We draw the robot if hes active
                if robot.is_active():
                    rx, ry, ro = robot.get_robot_thinks_position()
                    tx, ty = 15*math.cos(math.pi*2 *ro/360.0), 15*math.sin(math.pi*2 *ro/360.0)
                    pygame.draw.line(self.DISPLAYSURF, (255, 255, 0), (rx, ry), (rx+tx, ry+ty), 2)
                    pygame.draw.circle(self.DISPLAYSURF, (255, 255, 0), (rx, ry), 10)
                    name_tag_font = pygame.font.Font('freesansbold.ttf', 12)
                    name_tag = name_tag_font.render(str(robot.robot_id), True, (0, 0, 0))
                    name_tag_rect = name_tag.get_rect()
                    name_tag_rect.center = (rx, ry)
                    self.DISPLAYSURF.blit(name_tag, name_tag_rect)

            pygame.display.update()
            self.FPSCLOCK.tick(60)

    def determine_package_length(self, chrs):
        assert len(chrs) == 2
        return ord(chrs[0]) * 16 + ord(chrs[1])

    def calc_prefix_chars(self, length):
        a = length / 16
        b = length % 16
        prefix = chr(a) + chr(b)
        return prefix

    def send_message(self, sock, message, udp_info):
        total_len = len(message)
        assert total_len <= 255

        prefix = self.calc_prefix_chars(total_len)

        sock.sendto(prefix+message, udp_info)


ManualRobotPositionSetter()