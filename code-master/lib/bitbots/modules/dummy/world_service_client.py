import xmlrpclib


class WorldServiceClient(object):

    def __init__(self, host, port):
        self.proxy = xmlrpclib.ServerProxy("http://%s:%i/" % (host, port))

    def register_robot(self, robot_name):
        return self.proxy.register_robot(robot_name)

    def has_robot(self, name):
        return self.proxy.has_robot(name)

    def update_walking_for(self, player, f, s, a, active):
        return self.proxy.update_walking_for(player, f, s, a, active)

    def get_update_info(self, robotname):
        return self.proxy.get_update_info(robotname)

    def kick_ball(self, player):
        return self.proxy.kick(player)

    def set_running(self, val):
        return self.proxy.set_running(val)

    def kick_ball_side(self, player, direction):
        return self.proxy.kick_ball_side(player, direction)