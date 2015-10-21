from Queue import Queue
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
import threading
import pygame, time
import math
from RegistryClient import RegistryClient

WINDOWWIDTH = 900+70*2
WINDOWHEIGHT = 600+70*2
CPS = 100

ZERO_X = 450 + 70
ZERO_Y = 300 + 70

ENEMY_GOAL_X = 900 + 70
ENEMY_GOAL_Y = 300 + 70

OWN_GOAL_X = 70
OWN_GOAL_Y = 300 + 70

colours = {
    "glados": (255, 255, 0),
    "wheatly": (255, 0, 255),
    "atlas": (0, 0, 255),
    "tamara": (255, 0, 0),
    "wilma": (0, 255, 255),
    "fiona": (125, 0, 255)
}

class LocalGoalModelGUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        threading.daemon = True

        self.queue = Queue()
        self.player_positions = {}

    def __setattr__(self, name, value):
        return super(LocalGoalModelGUI, self).__setattr__(name, value)

    def send_debug_message_to_hub(self, type, name, value):
        print "Got Element"
        self.queue.put([type, name, value])
        return

    def dispatch_element(self, element):
        type, name, value = element

        robot, message = name.split("::")

        if robot not in self.player_positions:
            self.player_positions[robot] = [0, 0, 0]

        if "AbsolutePosition.x" in message:
            self.player_positions[robot][0] = int(int(value) / 10.0)

        if "AbsolutePosition.y" in message:
            self.player_positions[robot][1] = int(int(value) / 10.0)

        if "AbsolutePosition.o" in message:
            self.player_positions[robot][2] = int(value)

    def run(self):
        pygame.init()

        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.HWSURFACE)


        pygame.display.set_caption('RobotPositionTracker')

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

            while not self.queue.empty():
                element = self.queue.get()
                self.dispatch_element(element)
                print element

            for robot in self.player_positions:
                x, y, o = self.player_positions[robot]

                print robot, x, y, o

                c = colours.get(robot, (0, 0, 0))

                x += ZERO_X
                y += ZERO_Y

                xt = x + math.cos(2*math.pi*(o/360.))*10
                yt = y + math.sin(2*math.pi*(o/360.))*10

                pygame.draw.circle(self.DISPLAYSURF, (0,0,0), (x, y), 10)
                pygame.draw.line(self.DISPLAYSURF, c, (x, y), (xt, yt), 1)

                name_tag_font = pygame.font.Font('freesansbold.ttf', 14)
                name_tag = name_tag_font.render(str(robot), True, c)
                name_tag_rect = name_tag.get_rect()
                name_tag_rect.center = (x, y-40)
                self.DISPLAYSURF.blit(name_tag, name_tag_rect)

            pygame.display.update()
            self.FPSCLOCK.tick(60)
            time.sleep(0.2)

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

if __name__ == '__main__':

    productive = False
    if productive:
        registry_client = RegistryClient()
        assert registry_client.has_registered("AbsolutePositionShowClient"), "There is no AbsolutePositionShowClient"

        port_to_server = registry_client.get_port_by_name("AbsolutePositionShowClient")
    else:
        port_to_server = 55620
    server = SimpleXMLRPCServer(("localhost", port_to_server), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()

    local_goal_model_gui = LocalGoalModelGUI()
    local_goal_model_gui.start()
    server.register_instance(local_goal_model_gui)

    # Run the server's main loop
    server.serve_forever()