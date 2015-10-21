import os
import random
import unittest
import time
from bitbots.debug.debuglevels import DebugLevel


class ComplexObjectConverter(object):

    @staticmethod
    def convert_absolute_position_tuple(debug, key, element):
        Debug.debug_service_wrapper(debug, "%s.x" % key, element[0])
        Debug.debug_service_wrapper(debug, "%s.y" % key, element[1])
        Debug.debug_service_wrapper(debug, "%s.o" % key, element[2])

    @staticmethod
    def convert_ball_info(debug, key, element):
        Debug.debug_service_wrapper(debug, "%s.u" % key, element.u)
        Debug.debug_service_wrapper(debug, "%s.v" % key, element.v)
        Debug.debug_service_wrapper(debug, "%s.distance" % key, element.distance)

    @staticmethod
    def convert_nothing(debug, key, element):
        print "Nothing done for %s" % key

    @staticmethod
    def convert_goal_info(debug, key, element):
        if element is None:
            print "Element  for key %s is None so no further debugging" % key
            return

        u_fst, v_fst, u_sec, v_sec = None, None, None, None

        first_post = element.get(0, None)

        if first_post is not None:
            u_fst = first_post.u
            v_fst = first_post.v

        second_post = element.get(1, None)

        if second_post is not None:
            u_sec = second_post.u
            v_sec = second_post.v


        Debug.debug_service_wrapper(debug, key + ".1.u", u_fst)
        Debug.debug_service_wrapper(debug, key + ".1.v", v_fst)
        Debug.debug_service_wrapper(debug, key + ".2.u", u_sec)
        Debug.debug_service_wrapper(debug, key + ".2.v", v_sec)




class Debug(object):

    def __init__(self, update_time, list_of_data_keys):
        self.debug_level = int(os.getenv("DEBUG_LEVEL", 1))
        self.update_time = update_time
        self.list_of_data_keys = {
            e: list_of_data_keys[e] for e in list_of_data_keys if e <= self.debug_level
        }
        self.last_time = 0

    @staticmethod
    def debug_service_wrapper(debug, key, value):
        debug(key, value)

    def debug_it(self, debug, data):
        # Iterate over all the debug levels given in the dict
        for debug_level in self.list_of_data_keys:
            # Iterate over all data dict keys for the given debug level
            values_for_level = self.list_of_data_keys[debug_level]
            for value in values_for_level:
                if type(value) == tuple:
                    dict_key, converter = value
                    # It has a converter
                    if dict_key in data:
                        converter(debug, dict_key, data[dict_key])
                    else:
                        print "Key not in data dictionary", value
                else:
                    # It needs no converter
                    if value in data:
                        Debug.debug_service_wrapper(debug, value, data[value])
                    else:
                        print "Key not in data dictionary", value

    def __call__(self, function):
        def debug_wrapper(obj, data):
            # First call the update function
            result = function(obj, data)

            # Check if we need to make debug log calls
            if time.time() - self.last_time > self.update_time:
                self.last_time = time.time()
                self.debug_it(obj.debug, data)

            return result

        return debug_wrapper


class DummyDebugger(object):

    def __call__(self, *args):
        print args


class DummyModule():

    def __init__(self):
        self.debug = None

    def start(self, debug):
        self.debug = DummyDebugger()

    @Debug(update_time=2, list_of_data_keys={
        DebugLevel.DURING_GAME_DEBUG: ["SampleKey1"],
        DebugLevel.GAME_PREPARE_DEBUG: ["SampleKey2"],
    })
    def update(self, data):
        data["SampleKey1"] = random.random()
        data["SampleKey2"] = random.random()


class DebugAnnotationUnitTest(unittest.TestCase):

    def test(self):
        mydata = {}
        mydebug = DummyDebugger()

        do = DummyModule()
        do.start(mydebug)

        for i in range(1000):
            do.update(mydata)
            time.sleep(0.01)