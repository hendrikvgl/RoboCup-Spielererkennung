#-*- coding:utf-8 -*-
"""
MotorView
^^^^^^^^^^

Implementation of the MotorView, which, opens the Motorview.glade-data and implements all the neccessary methods to
show the information of the robots about the motors.


:platform: Unix and Windows

.. moduleauthor:: Robocup-AG in cooperation with Projekt-Debug-UI (implemented by Nils Rokita and partly old Code)

.. autoclass:: MotorView(GenericNotebookView)
    :members:
"""
from genericView import GenericNotebookView
from motorTemp import MotorTempGraph
#import pylab as p
import gtk

from debuguineu.functions import make_ui_proxy, find, beep

from bitbots.util import get_error_list

import time
import gobject

MOTOR_NAME = ("platzhalter", "r_shoulder_pitch", "l_shoulder_pitch", "r_shoulder_roll", "l_shoulder_roll", "r_elbow", "l_elbow", "r_hip_yaw", "l_hip_yaw", "r_hip_roll", "l_hip_roll", "r_hip_pitch", "l_hip_pitch", "r_knee", "l_knee", "r_ankle_pitch", "l_ankle_pitch", "r_ankle_roll", "l_ankle_roll", "head_pan", "head_tilt")
error_ids = ['Unzulässige Spannung', 'Unzulässiger Zielwinkel', 'Überhitzung', 'Command Range-Error', 'Checksum-Error', 'Überlastung', 'Fehlerhafte Anweisung', 'Überraschungsfehler']

class WarningWindow(object):
    def __init__(self):
        self.builderWwin = gtk.Builder()
        self.builderWwin.add_from_file(
            find("Projekt_DebugUI_Warnfenster.glade"))
        #das Warnfenster.  muss eigentlich bei Fehlern aufgerufen werden
        #sobald die Errorbits funzen kann also das Warnfenster zusammen mit einem auftretenden
        #Fehler aufgerufen werden
        self.wWindow = self.builderWwin.get_object(
            "messagedialogWarnfenster")
        self.builderWwin.connect_signals(self)

    def show(self, text):
        self.builderWwin.get_object("labelProblemArt").set_markup(text)
        self.wWindow.show()
        self.aktive = True
        #beep() # das braucht zuuu lange und blockiert damit alles

    def on_messagedialogWarnfenster_destroy(self, *args):
        """
        Closes the warning popup window.
        """
        print args
        print ("Schliessen des Warnfensters wurde gedrueckt")
        self.wWindow.destroy()
        self.aktive = False

    def on_buttonProblemZeigen_clicked(self, *args):
        """
        Shows the reason the popup popped up. Currently opens the Motor View.
        """
        self.wWindow.destroy()
        self.aktive = False
        print "Das geht noch garnicht"


class MotorView(GenericNotebookView):
    """
    This Class generates a View for the motors of the robot
    """
    def __init__(self, data_callback, view_calback):
        """
        Inits the View

        :param add_observer: a callbackfunction to register observer in the datamodel from mainwindow
        :type add_observer: function
        """
        super(MotorView, self).__init__("Motor View",
                                        data_callback, view_calback)
        self.motorviews = {}
        self.robots = []
        self.motortmps = {}
        self.voltage = {}
        self.last_update_label = None
        self.last_update = {}
        self.warnings=[]
        self.last_update_label = {}
        #fig = p.figure()
        self.ax = None #fig.add_subplot(111)

    def add_new_robot(self, name):
        """
        this Function adds a new robot to the View, creates the nessesary widgets and register the observers

        :param robot: Name of the Robot
        :type name: String
        """
        builder_int = gtk.Builder()
        builder_int.add_objects_from_file(
            find("Projekt_DebugUI_Motor_View.glade"), ("MotorView",))
        motor_view_int = builder_int.get_object('MotorView')

        for i in range(1, 21):
            motor = builder_int.get_object('motor' + str(i))
            print motor
            motor.set_name("%02d%s" % (i, name))
        cm = builder_int.get_object('volt_cm730')
        cm.set_name("cm%s" % name)

        builder_ext = gtk.Builder()
        builder_ext.add_objects_from_file(
            find("Projekt_DebugUI_Motor_View.glade"), ("MotorView",))
        motor_view_ext = builder_ext.get_object('MotorView')

        self.last_update_label[name + "_int" ] = builder_int.get_object(
            "lastUpdate")
        self.last_update_label[name + "_ext" ] = builder_ext.get_object(
            "lastUpdate")
        self.last_update[name + '_int'] = 0
        self.last_update[name + '_ext'] = 0
        gobject.timeout_add(1000, self.update_last_update_label, name + "_int")
        gobject.timeout_add(1000, self.update_last_update_label, name + "_ext")

        self.add_notebook_page(name, motor_view_int, motor_view_ext)

        self.motorviews[name + "_int"] = make_ui_proxy(builder_int)
        self.motorviews[name + "_ext"] = make_ui_proxy(builder_ext)

        self.register_observers(name, self.data_callback)

        self.robots.append(name)

        builder_int.connect_signals(self)
        builder_ext.connect_signals(self)

        self.motortmps[name] = {}
        self.voltage[name] = [[], []]

    def register_observers(self, robot, register):
        """ Registers all observers for the robot when called"""

        # make update functions for given motor
        def make_temp_callback(nr):
            return lambda item: self.update_motor_temp(item, nr, robot)
        #def make_volt_callback(nr):
        #    return lambda item: self.update_motor_volt(item, nr)

        def make_error_callback(nr):
            return lambda item: self.update_motor_error(item, nr)

        #functions registerd per dynamixel-motor:
        for idx in range(1, 21):
            prop = "%s::Motion.Server.MX28.%d.Temperatur" % (robot, idx)
            register(prop, make_temp_callback(idx))
            #prop = "%s::Motion.Server.MX28.%d.Voltage" % (robot, idx)
            #register(prop, make_volt_callback(idx))

        #functions registered once:
        prop = "%s::Motion.Server.CM730.Voltage" % robot
        register(prop, (lambda item: self.update_cm730_volt(item, robot)))

        prop = "%s::Controller.LastError" % robot
        register(prop, (lambda item: self.update_motor_error(item, robot)))

        prop = "%s::Motion.Server.Updates/Sec" % robot
        register(prop, (lambda item : self.update_last_update(robot, item)))

    def update_label_and_color(self, color, motor_id, text, robot):
        """ Helper function to set a motor buttons color
        """
        button_int = self.motorviews[robot + "_int"].get(
            "motor%d" % (motor_id))
        button_ext = self.motorviews[robot + "_ext"].get(
            "motor%d" % (motor_id))

        self.set_button_color(button_int, color)
        self.set_button_color(button_ext, color)

        label = "" + str(
            motor_id) + " T: " + str(text) + "\n" + str(MOTOR_NAME[motor_id])
        button_int.set_label(label)
        button_ext.set_label(label)

    def update_motor_temp(self, item, motor_id, robot):
        """calculate color of the buttons who represent the motors
        temperatures of 30 or below are green (0,255,0)RGB
        temperatures of 60 or higher are red (255,0,0)RGB
        temperatures in between gradually shift their values from green to red
        """
        if item is None or item.type != "number":
            return

        temp = item.value
        if temp < 0:
            color = (0, 0, 0)
        elif temp < 30:
            color = (0, 65355, 0)
        elif temp > 60:
            color = (65535, 0, 0)
        else:
            colormod = (temp - 30) * 65535 / 30
            color = (colormod, 65535 - colormod, 0)

        self.update_label_and_color(color, motor_id, temp, robot)

        if motor_id not in self.motortmps[robot]:
            self.motortmps[robot][motor_id] = [0, 1]
            self.motortmps[robot][motor_id][0] = []
            self.motortmps[robot][motor_id][1] = []

        self.motortmps[robot][motor_id][0].append(item.value)
        self.motortmps[robot][motor_id][1].append(time.time())

    def set_button_color(self, button, color):
        gtkColor = gtk.gdk.Color(*color)
        button.modify_bg(gtk.STATE_NORMAL, gtkColor)
        button.modify_bg(gtk.STATE_ACTIVE, gtkColor)
        button.modify_bg(gtk.STATE_PRELIGHT, gtkColor)
        button.modify_bg(gtk.STATE_SELECTED, gtkColor)

    def update_cm730_volt(self, item, robot):
        """calculate the color of the button which represents the cm730
        see update_motor_volt
        """
        if item is None or item.type != "number":
            return
        volt = item.value
        if volt > 120:
            colormod = min(((volt - 120) * 65535 / 40), 65535)
            color = (colormod, 65535 - colormod, 0)
        elif volt <= 120:
            colormod = min(((120 - volt) * 65535 / 30), 65535)
            color = (0, 65535 - colormod, colormod)

        button_int = self.motorviews[robot + "_int"].get("volt_cm730")
        button_ext = self.motorviews[robot + "_ext"].get("volt_cm730")
        bar_int = self.motorviews[robot + "_int"].get("batteryStatusBar")
        bar_ext = self.motorviews[robot + "_ext"].get("batteryStatusBar")
        #print min(1, max(0, float(volt - 110) / 14)), float(volt - 110) / 14, (volt - 110)
        battery = min(1, max(0, float(volt - 110) / 14))  # TODO: Formel Prüfen
        bar_int.set_fraction(battery)
        bar_ext.set_fraction(battery)

        self.set_button_color(button_int, color)
        self.set_button_color(button_ext, color)

        label = "CM_730\n" + str(volt)
        button_int.set_label(label)
        button_ext.set_label(label)

        self.voltage[robot][0].append(item.value)
        self.voltage[robot][1].append(time.time())

    def update_motor_error(self, item, robot):
        """Update the Error view to show the last received Error
        """
        if item is None or item.type != "number":
            return
        cid = item.value & 0xFF
        error = item.value >> 8
        message = get_error_list(error)
        #label = self.ui.get("lastError")
        #label.set_markup("<span foreground='red'>%s</span>"%message)
        print "bik"
        self.warnings.append(
            WarningWindow().show("Motor %d Robot %s hat einen Fehler: %s" % (cid, robot, message)))
        for w in self.warnings[:]:
            if not w.aktive:
                pass
                #TODO: del!

    def update_last_update(self, robot, *args):
        """ Save last update time, as soon as we receive a new package
        """
        self.last_update[robot + "_int"] = time.time()
        self.last_update[robot + "_ext"] = time.time()

    def update_last_update_label(self, robot):
        """ Update the Lable to display how long the last package is ago
        :param robot: robtername inklusive _int und _ext für die view
        """
        max_delay = 30
        timedelta = int(time.time() - self.last_update[robot])
        if timedelta is 0:
            red = 0
            green = 255
        elif timedelta > max_delay:
            red = 255
            green = 0
        else:
            red = 0 + 255 / max_delay * timedelta
            green = 255 - 255 / max_delay * timedelta
        rgb_tuple = (red, green, 0)
        hexcolor = '#%02x%02x%02x' % rgb_tuple
        self.last_update_label[robot].set_markup(
            "<span foreground='%s'>%i seconds ago</span>" % (
                hexcolor, timedelta))
        return True

    def get_internal_state(self):
        state = {'MotorView.robots': self.robots}
        state.update(super(MotorView, self).get_internal_state())
        return state

    def set_internal_state(self, state):
        super(MotorView, self).set_internal_state(state)
        for robot in state['MotorView.robots']:
            self.add_new_robot(robot)

    def on_motor_clicked(self, *args):
        #motor = args[0]
        try:
            motor = int(args[0].get_name()[:2])
            robot = args[0].get_name()[2:]
            data = (self.motortmps[robot][motor][1], self.motortmps[robot][motor][0])
            text = "%s: Temperatur Motor %d" % (robot, motor)
            graphThread = MotorTempGraph(data, text, self.ax)
            graphThread.start()
        except Exception as e:
            print "Fehler beim anzeigen der Motorgraphen", e

    def on_volt_clicked(self, *args):
        #motor = args[0]
        try:
            robot = args[0].get_name()[2:]
            data = (self.voltage[robot][1], self.voltage[robot][0])
            text = "%s: Voltage" % robot
            graphThread = MotorTempGraph(data, text, self.ax)
            graphThread.start()
        except:
            print "Fehler beim anzeigen der Motorgraphen"
