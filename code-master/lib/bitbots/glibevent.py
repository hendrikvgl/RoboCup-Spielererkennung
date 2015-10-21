#-*- coding:utf-8 -*-

import sys
import gtk
import gobject
import gevent


def glib_gevent_loop():
    def idle():
        try:
            gevent.sleep(0.04)
        except:
            gtk.main_quit()
            gevent.hub.MAIN.throw(*sys.exc_info())
        
        return True   
    gobject.idle_add(idle)
    gtk.main()

