from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
from multiprocessing import Queue
import threading
import pygame
import time
from RegistryClient import RegistryClient


CONFIGURED_ROBOTS = ["glados", "wheatly", "atlas", "tamara", "wilma", "fiona", "sheepy-laptop"]
HEIGHT_FACTOR = 20
WIDTH = 120

class RobotKeepAliveGUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.robots_info = {
            name: 0 for name in CONFIGURED_ROBOTS
        }

        self.message_queue = Queue()

    def send_got_message_from_robot(self, robot_name):
        self.message_queue.put(robot_name)

    def run(self):
        pygame.init()

        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WIDTH*2, HEIGHT_FACTOR*len(CONFIGURED_ROBOTS)), pygame.HWSURFACE)


        pygame.display.set_caption('RobotKeepAlive')

        while True:
            pygame.draw.rect(self.DISPLAYSURF, (0, 0, 0), pygame.Rect(0, 0, HEIGHT_FACTOR, len(CONFIGURED_ROBOTS)))

            # draw the slots where the robots are displayed
            counter = 0
            for key in CONFIGURED_ROBOTS:
                last_time = self.robots_info[key]
                delta_from_now = time.time() - last_time

                if delta_from_now < 5:
                    colour = (0, 255, 0)
                elif delta_from_now < 10:
                    colour = (255, 125, 0)
                else:
                    colour = (255, 0, 0)

                x = 0
                y = counter

                pygame.draw.rect(self.DISPLAYSURF, colour, pygame.Rect(x, HEIGHT_FACTOR*y, WIDTH, HEIGHT_FACTOR))
                pygame.draw.rect(self.DISPLAYSURF, colour, pygame.Rect(WIDTH, HEIGHT_FACTOR*y, WIDTH, HEIGHT_FACTOR))
                pygame.draw.rect(self.DISPLAYSURF, (100, 100, 100), pygame.Rect(x, HEIGHT_FACTOR*y, 2*WIDTH, HEIGHT_FACTOR), 1)


                name_tag_font = pygame.font.Font('freesansbold.ttf', 14)
                name_tag = name_tag_font.render(str(key), True, (0, 0, 0))
                name_tag_rect = name_tag.get_rect()
                name_tag_rect.center = (x+WIDTH/2, y*HEIGHT_FACTOR+HEIGHT_FACTOR/2)
                self.DISPLAYSURF.blit(name_tag, name_tag_rect)


                time_string = "Last was " + str(min(99, int(delta_from_now)))
                name_tag = name_tag_font.render(str(time_string), True, (0, 0, 0))
                name_tag_rect = name_tag.get_rect()
                name_tag_rect.center = (WIDTH+WIDTH/2, y*HEIGHT_FACTOR+HEIGHT_FACTOR/2)
                self.DISPLAYSURF.blit(name_tag, name_tag_rect)

                counter += 1

            # Refresh the timestamps
            while not self.message_queue.empty():
                robot_name = self.message_queue.get()

                if robot_name in self.robots_info:
                    self.robots_info[robot_name] = time.time()

            pygame.display.update()
            self.FPSCLOCK.tick(20)

        print "End of while"




class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == '__main__':

    registry_client = RegistryClient()
    assert registry_client.has_registered("RobotKeepAliveClient"), "There is no RobotKeepAliveClient"

    port_to_server = registry_client.get_port_by_name("RobotKeepAliveClient")

    server = SimpleXMLRPCServer(("localhost", port_to_server), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()

    robot_keep_alive_gui = RobotKeepAliveGUI()
    robot_keep_alive_gui.start()
    server.register_instance(robot_keep_alive_gui)

    # Run the server's main loop
    server.serve_forever()