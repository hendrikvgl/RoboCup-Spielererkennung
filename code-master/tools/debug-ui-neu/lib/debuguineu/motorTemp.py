#-*- coding:utf-8 -*-
import threading
#from matplotlib import pyplot as plt
import time
import pylab as p
import thread

class MotorTempGraph(threading.Thread):
    def __init__(self, data, name, ax):
        threading.Thread.__init__(self)
        self.data = data
        self.grap_name = name
        self.ax = ax

    def run(self):
        try:
            #fig = p.figure()
            #self.ax = fig.add_subplot(111)
            self.plot, = p.plot(self.data[0], self.data[1])
            self.plot.set_label(self.grap_name)
            print self.plot
            thread.start_new_thread(self.update, ())
            p.ylabel('Temperatur in °C')
            p.xlabel('Zeit in s')
            p.legend()
            p.show()
        except Exception as e:
            print "Fehler beim anzeigen der Motorgraphen:", e

    def update(self):
        while True:
            time.sleep(1)
            print self.data[0]
            self.plot.set_xdata(self.data[0])
            self.plot.set_ydata(self.data[1])
            print p.gca()
            self.ax = p.gca()
            self.ax.relim()
            self.ax.autoscale_view(True,True,True)
            p.draw()
