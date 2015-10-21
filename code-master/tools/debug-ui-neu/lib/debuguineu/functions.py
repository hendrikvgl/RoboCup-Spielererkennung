#-*- coding:utf-8 -*-
import sys
platform = sys.platform
if platform == 'win32':
    import winsound
elif platform == 'linux2':
    import os


from bitbots.util import generate_find, find
try:
    find('share/debug-ui-neu')
    find = generate_find('share/debug-ui-neu')
except:
    # legacy für entwickeln ohne virtualenv
    find = generate_find('tools/debug-ui-neu/share/debug-ui-neu')


def make_ui_proxy(builder):
    class UIProxy(object):
        def __getattr__(self, name):
            result = builder.get_object(name)
            if result is None:
                raise KeyError(name + " not a valid ui-object")

            setattr(self, name, result)
            return result

        def get(self, name):
            return getattr(self, name)

        def has(self, name):
            return builder.get_object(name) is not None

    return UIProxy()

def beep():
    """
    Global method, implemented to give an acoustic signal when a warning
    pops up.
    """
    if platform == 'win32':
        winsound.PlaySound(find("sound/beepPing.wav"), winsound.SND_ASYNC)
    elif platform == 'linux2':
        os.system('aplay %s' % find("sound/beepPing.wav"))
    print("Beep!")
