#-*- coding:utf-8 -*-
"""
.. warning::
    Es _müssen_ die folgenden umgebungsvariablen gesetzt sein:
    DEBUG=1 DEBUG_HOST=localhost DEBUG_PORT=60445
    werden von `run-python-unittests-old` themporär gesetzt
"""

import unittest


from bitbots.debug import Scope
from bitbots.debug import debugserver

import gevent
import socket
PORT = 60445
HOST = socket.gethostname()
class DebugNetListener(object):
    def __init__(self):
        self.data = {}
        self.server = debugserver.Server(("",PORT))
        self.server.add_listener(self.data_callback)
        self.server.start()

    def data_callback(self, type, name, value):
        self.data[name] = (type, value)

    def get_debug_data(self, name):
        return self.data.get(name, False)

    def reset(self):
        gevent.sleep(1)  # Warten auf etwagig abwarten
        self.data = {} # daten lehren


class TestDebugFramework(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        print "#### Test Debug Framework ####"
        cls.dbg = DebugNetListener()


    def test_create_Scope(self):
        test = Scope('Test')
        self.assertEquals(test.get_name(), 'Test')
        self.assertTrue(test.get_console_out())
        test2 = Scope('Test', False)
        self.assertEquals(test2.get_name(), 'Test')
        self.assertFalse(test2.get_console_out())
        test3 = Scope('Test.hui')
        self.assertEquals(test3.get_name(), 'Test.hui')

    def test_create_sub_Scope(self):
        test = Scope('Test')
        test_sub1 = test.sub('sub1')
        self.assertEquals(test_sub1.get_name(), 'Test.sub1')
        test_sub2 = test.sub('SUB2')
        self.assertEquals(test_sub2.get_name(), 'Test.SUB2')
        test_sub3 = test_sub1.sub('bla')
        self.assertEquals(test_sub3.get_name(), 'Test.sub1.bla')

    def test_net_console_log_call(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug('Testnachricht')
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.log")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "log")
        self.assertEquals(msg[1], "Testnachricht")

        debug('Dies ist eine längere Nachricht')
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.log")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "log")
        self.assertEquals(msg[1], "Dies ist eine längere Nachricht")

    def test_net_console_log(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug.log('Testnachricht')
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.log")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "log")
        self.assertEquals(msg[1], "Testnachricht")

        debug.log('Dies ist eine längere Nachricht')
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.log")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "log")
        self.assertEquals(msg[1], "Dies ist eine längere Nachricht")

    def test_net_console_log_lshift(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug << 'Testnachricht'
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.log")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "log")
        self.assertEquals(msg[1], "Testnachricht")

        debug << 'Dies ist eine längere Nachricht'
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.log")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "log")
        self.assertEquals(msg[1], "Dies ist eine längere Nachricht")

    def test_net_console_warning(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug.warning('Testnachricht')
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.warning")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "warning")
        self.assertEquals(msg[1], "Testnachricht")

        debug.warning('Dies ist eine längere Nachricht')
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.warning")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "warning")
        self.assertEquals(msg[1], "Dies ist eine längere Nachricht")

    def test_net_error(self):
        self.dbg.reset()
        debug = Scope('Test')
        try:
            raise Exception("This is a Test Exception")
        except Exception as e:
            debug.error(e)
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.warning")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "warning")
        # wir können hier so nur auf die 2. nachricht zugreifen (momentan traceback)
        self.assertTrue("This is a Test Exception" in msg[1]) # traceback im msg

    def test_net_error_prefix(self):
        self.dbg.reset()
        debug = Scope('Test')
        try:
            raise Exception("This is a Test Exception")
        except Exception as e:
            debug.error(e, "Testprefix: ")
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.warning")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "warning")
        # wir können hier so nur auf die 2. nachricht zugreifen (momentan traceback)
        self.assertTrue("This is a Test Exception" in msg[1]) # traceback im msg


    def test_net_send_string(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug("Name", "Toller Name mit Umlauten: öä")
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Name")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "string")
        self.assertEquals(msg[1], "Toller Name mit Umlauten: öä")

    def test_net_send_string_log(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug.log("Name", "Toller Name mit Umlauten: öä")
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Name")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "string")
        self.assertEquals(msg[1], "Toller Name mit Umlauten: öä")

    def test_net_send_int(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug("Number", 1254)
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Number")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "number")
        self.assertEquals(msg[1], 1254)
        debug("Number", -45)
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Number")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "number")
        self.assertEquals(msg[1], -45)
        debug("Number", -45687645)
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Number")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "number")
        self.assertEquals(msg[1], -45687645)

    def test_net_send_float(self):
        self.dbg.reset()
        debug = Scope('Test')
        debug("Number", 1.5)
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Number")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "number")
        self.assertEquals(msg[1], 1.5)
        debug("Number", -45.458964)
        gevent.sleep(1)
        msg = self.dbg.get_debug_data(HOST + "::Test.Number")
        self.assertTrue(msg) # es ist keine nachricht angekommen
        self.assertEquals(msg[0], "number")
        self.assertEquals(round(msg[1],4), round(-45.458964,4))

if __name__ == '__main__':
    unittest.main()
