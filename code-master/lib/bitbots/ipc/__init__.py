from bitbots.ipc.ipc import *


def connect(server=False):
    """

    :param server:
    :return:
    """
    return SharedMemoryIPC(not server)

