import sys

sys.path.append(sys.path[0]+"/lib")
#sys.path.append(sys.path[0]+"/tools/debug-ui/bin")
#sys.path.append(sys.path[0]+"/tools/debug-ui/lib")
sys.path.append(sys.path[0]+"/tools/debug-ui-neu/lib/debuguineu")
sys.path.append(sys.path[0]+"/tools/debug-ui-neu/lib")
sys.path.append(sys.path[0]+"/tools/debug-ui-neu/bin")
#sys.path.append(sys.path[0]+"/MEIN_ORDNERfuerRobocupDebugUI")


import time
#from debugui.mainwin import DebugMainWindow
from mainwindow import DebugUiMainWin
import sys
import gevent
import bitbots.glibevent
import gzip
print sys.path
import pickle

fp = gzip.GzipFile("/home/annika/debug-1358949977.919242.gz")

#hier die zwei neuen Fakeserverdaten :) bei dem ersten kommt nach etwa 10min n Fehler, beim zweiten sollten zwei Robos sein
#fp = gzip.GzipFile("/home/annika/debug-1363790604.066494.gz")
#fp = gzip.GzipFile("/home/annika/debug-1363792927.388008.gz")

#fp = sys.stdin

class FakeServer(object):
    listener = None
    def add_listener(self, li):
        self.listener = li

    def start(self):
        offset = None
        while True:
            stamp, values = pickle.load(fp)
            if offset is None:
                offset = time.time() - stamp

            diff = stamp + offset - time.time()

            if diff > 0:
                gevent.sleep(diff)

            self.listener(*values)

server = FakeServer()
gevent.spawn_later(1, server.start)

win = DebugUiMainWin(server)
win.show()

bitbots.glibevent.glib_gevent_loop()

#import debugui.mainwin
