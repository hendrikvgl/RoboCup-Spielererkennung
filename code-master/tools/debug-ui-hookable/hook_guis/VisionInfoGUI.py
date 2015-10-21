from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
from multiprocessing import Queue
from RegistryClient import RegistryClient
import threading
import pygame

CONFIGURED_ROBOTS = ["glados", "wheatly", "atlas", "tamara", "wilma", "fiona", "sheepy-laptop"]
HEIGHT_FACTOR = 30
WIDTH = 120
STATUS_WIDTH = 40


class RobotStatus(object):

    def __init__(self, name):
        self.name = name
        self.goal_found = 0
        self.obstacles = 0
        self.ball_found = 0

    def __repr__(self):
        return super(RobotStatus, self).__repr__()


class VisionInfoGUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.goal = pygame.image.load('resources/goal.png')
        self.ball = pygame.image.load('resources/ball.png')
        self.obstacle = pygame.image.load('resources/obstacle.png')

        self.robots_info = {
            name: RobotStatus(name) for name in CONFIGURED_ROBOTS
        }

        self.message_queue = Queue()

    def send_got_message_from_robot(self, type, name, value):
        self.message_queue.put([type, name, value])

    def dispatch(self, element):
        type, name, value = element

        robot = name.split("::")[0]

        if robot not in self.robots_info:
            return

        robot_status = self.robots_info[robot]

        if "GoalFound" in name:
            robot_status.goal_found = int(value)
        elif "Obstacles" in name:
            robot_status.obstacles = int(value)
        elif "BallFound" in name:
            robot_status.ball_found = int(value)
        else:
            print "Not Filtered", name

    def run(self):
        pygame.init()

        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WIDTH+3*STATUS_WIDTH, HEIGHT_FACTOR*len(CONFIGURED_ROBOTS)), pygame.HWSURFACE)


        pygame.display.set_caption('VisionInfoGUI')

        while True:
            # Clear screen
            pygame.draw.rect(self.DISPLAYSURF, (0, 0, 0), pygame.Rect(0, 0, WIDTH+3*STATUS_WIDTH, HEIGHT_FACTOR*len(CONFIGURED_ROBOTS)))

            # draw the slots where the robots are displayed
            counter = 0
            for key in CONFIGURED_ROBOTS:
                robot_status = self.robots_info[key]

                colour = (255, 255, 255)
                pygame.draw.rect(self.DISPLAYSURF, colour, pygame.Rect(0, HEIGHT_FACTOR*counter, WIDTH+3*STATUS_WIDTH, HEIGHT_FACTOR))
                pygame.draw.rect(self.DISPLAYSURF, (100, 100, 100), pygame.Rect(0, HEIGHT_FACTOR*counter, WIDTH, HEIGHT_FACTOR), 1)
                pygame.draw.rect(self.DISPLAYSURF, (100, 100, 100), pygame.Rect(WIDTH, HEIGHT_FACTOR*counter, STATUS_WIDTH, HEIGHT_FACTOR), 1)
                pygame.draw.rect(self.DISPLAYSURF, (100, 100, 100), pygame.Rect(WIDTH+STATUS_WIDTH, HEIGHT_FACTOR*counter, STATUS_WIDTH, HEIGHT_FACTOR), 1)
                pygame.draw.rect(self.DISPLAYSURF, (100, 100, 100), pygame.Rect(WIDTH+2*STATUS_WIDTH, HEIGHT_FACTOR*counter, STATUS_WIDTH, HEIGHT_FACTOR), 1)

                name_tag_font = pygame.font.Font('freesansbold.ttf', 14)
                name_tag = name_tag_font.render(str(key), True, (0, 0, 0))
                name_tag_rect = name_tag.get_rect()
                name_tag_rect.center = (WIDTH/2, counter*HEIGHT_FACTOR+HEIGHT_FACTOR/2)
                self.DISPLAYSURF.blit(name_tag, name_tag_rect)

                if robot_status.ball_found:
                    rect = pygame.Rect(WIDTH, counter*HEIGHT_FACTOR, STATUS_WIDTH, HEIGHT_FACTOR)
                    self.DISPLAYSURF.blit(self.ball, rect)

                if robot_status.goal_found:
                    rect = pygame.Rect(WIDTH+STATUS_WIDTH, counter*HEIGHT_FACTOR, STATUS_WIDTH, HEIGHT_FACTOR)
                    self.DISPLAYSURF.blit(self.goal, rect)

                if robot_status.obstacles:
                    rect = pygame.Rect(WIDTH+2*STATUS_WIDTH, counter*HEIGHT_FACTOR, STATUS_WIDTH, HEIGHT_FACTOR)
                    self.DISPLAYSURF.blit(self.obstacle, rect)

                counter += 1

            # Refresh the timestamps
            while not self.message_queue.empty():
                element = self.message_queue.get()

                self.dispatch(element)

            pygame.display.update()
            self.FPSCLOCK.tick(20)

        print "End of while"




class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == '__main__':

    registry_client = RegistryClient()
    assert registry_client.has_registered("VisionInfoClient"), "There is no VisionInfoClient"

    port_to_server = registry_client.get_port_by_name("VisionInfoClient")

    server = SimpleXMLRPCServer(("localhost", port_to_server), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()

    vision_info_gui = VisionInfoGUI()
    vision_info_gui.start()
    server.register_instance(vision_info_gui)

    # Run the server's main loop
    server.serve_forever()

