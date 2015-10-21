import time

class Timer(object):
    __slots__ = ("name", "start", "debug")

    def __init__(self, name, debug):
        self.name = name
        self.start = None
        self.debug=debug

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *ignore):
        duration = 1000 * (time.time() - self.start)
        self.debug(self.name, "brauchte %1.2fms" % duration)
