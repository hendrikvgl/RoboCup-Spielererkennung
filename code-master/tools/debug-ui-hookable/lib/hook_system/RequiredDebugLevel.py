# -*- coding:utf-8 -*-

class RequiredDebugLevel(object):

    def __init__(self, required_debug_level, actual_debug_level):
        self.required_debug_level = required_debug_level
        self.actual_debug_level = actual_debug_level

    def __call__(self, f):
        def wrapped_function(clazz):

            if self.required_debug_level >= self.actual_debug_level:
                f(clazz)
            else:
                print "Don't executed", str(f), "due to debug level."

        return wrapped_function

