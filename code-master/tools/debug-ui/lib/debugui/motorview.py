#-*- coding:utf-8 -*-
import gtk
from bitbots.util import find_resource as find
from functions import make_ui_proxy

MOTOR_NAME = ("platzhalter", "r_shoulder_pitch", "l_shoulder_pitch", "r_shoulder_roll", "l_shoulder_roll", "r_elbow", "l_elbow", "r_hip_yaw", "l_hip_yaw", "r_hip_roll", "l_hip_roll", "r_hip_pitch", "l_hip_pitch", "r_knee", "l_knee", "r_ankle_pitch", "l_ankle_pitch", "r_ankle_roll", "l_ankle_roll", "head_pan", "head_tilt")

error_ids = ['Unzulässige Spannung','Unzulässiger Zielwinkel', 'Überhitzung', 'Command Range-Error', 'Checksum-Error', 'Überlastung', 'Fehlerhafte Anweisung','Überraschungsfehler']

class MotorView(object):
    """ Provides Graphical visualisation of the Robot
    like Motor Temperatures, Voltages, arriving Errors
    """
    def __init__(self, destroy):
        self.destroy = destroy
        self.setup_ui()

    def setup_ui(self):
        # .ui-files can be edited using "glade" 
        builder = gtk.Builder()
        builder.add_from_file(find("debug.motor.ui"))
        builder.connect_signals(self)
        
        self.ui = make_ui_proxy(builder)
        self.ui.window.show()
        
    def on_delete_event(self, *ignore):
        self.destroy()

    def on_destroy_event(self, *ignore):
        self.destroy()

    def register_observers(self, name, register):
        """ Registers all observers for this class when called"""
        
        # make update functions for given motor
        def make_temp_callback(nr):
            return lambda item: self.update_motor_temp(item, nr)
        def make_volt_callback(nr):
            return lambda item: self.update_motor_volt(item, nr)
        def make_error_callback(nr):
            return lambda item: self.update_motor_error(item,nr)

        host = name.split("::")[0] #"name" starts with hostname::

        #functions registerd per dynamixel-motor:
        for idx in range(1, 21):
            prop = "%s::Motion.Server.MX28.%d.Temperatur" % (host, idx)
            register(prop, make_temp_callback(idx))
            prop = "%s::Motion.Server.MX28.%d.Voltage" % (host, idx)
            register(prop, make_volt_callback(idx))

        #functions registered once:
        prop = "%s::Motion.Server.CM730.Voltage" % host
        register(prop,(lambda item: self.update_cm730_volt(item)))
        prop = "%s::Motion.Server.Voltage.Max" % host
        register(prop,(lambda item: self.update_max_volt(item)))
        prop = "%s::Motion.Server.Voltage.Min" % host
        register(prop,(lambda item: self.update_min_volt(item)))
        prop = "%s::Motion.Server.Temperatur.Max" % host
        register(prop,(lambda item: self.update_max_temp(item)))
        prop = "%s::Motion.Server.Temperatur.Max.Cid" % host
        register(prop,(lambda item: self.update_max_temp_origin(item)))
        prop = "%s::Module.Controller.GoalColor" % host
        register(prop,(lambda item: self.update_goal(item)))
        prop = "%s::Controller.LastError.Motor" % host
        register(prop,(lambda item: self.update_motor_error(item)))
        prop = "%s::Controller.LastError.Bit" % host
        register(prop,(lambda item: self.update_motor_error_id(item)))
        
    def update(self, item):
        """ Nothing to do here anymore"""
        pass
    
    def update_label_and_color(self, color, motor_id, text):
        """ Helper function to set a motor buttons color
        """
        button = self.ui.get("motor%d" % (motor_id))
        gtkColor = gtk.gdk.Color(*color)
        button.modify_bg(gtk.STATE_NORMAL, gtkColor) 
        button.modify_bg(gtk.STATE_ACTIVE, gtkColor) 
        button.modify_bg(gtk.STATE_PRELIGHT, gtkColor) 
        button.modify_bg(gtk.STATE_SELECTED, gtkColor)
        
        if motor_id > 20:
            mid = motor_id - 20
        else:
            mid = motor_id
            
        label = str(motor_id) + "\n" + str(MOTOR_NAME[mid]) + "\n" + str(text)
        button.set_label(label)
        
    def update_motor_temp(self, item, motor_id):
        """calculate color of the buttons who represent the motors
        temperatures of 30 or below are green (0,255,0)RGB
        temperatures of 60 or higher are red (255,0,0)RGB
        temperatures in between gradually shift their values from green to red
        """
        if item is None or item.type != "number":
            return
        
        temp = item.value
        if temp < 0 : 
            color =(0,0,0)
        elif temp < 30:
            color = (0,65355,0)
        elif temp > 60: 
            color = (65535,0,0)
        else:
            colormod = (temp - 30) * 65535/30 
            color = (colormod,65535-colormod,0)
        
        self.update_label_and_color(color, motor_id, temp)
        
    def update_motor_volt(self, item, motor_id):
        """calculate color of the buttons who represent the motors
        voltage 12 is green
        higher voltage is red
        lower voltage is blue"""
        if item is None or item.type != "number":
            return
        
        volt = item.value
        if volt > 120:
            colormod = min(((volt -120) * 65535/40), 65535)
            color = (colormod, 65535-colormod,0)
        elif volt <= 120:
            colormod = min(((120-volt) * 65535/30), 65535)
            color = (0, 65535-colormod, colormod)

        self.update_label_and_color(color, motor_id + 20, volt)

    def update_cm730_volt(self, item):
        """calculate the color of the button which represents the cm730
        see update_motor_volt
        """
        if item is None or item.type != "number":
            return
        volt = item.value
        if volt > 120:
            colormod = min(((volt -120) * 65535/40), 65535)
            color = (colormod, 65535-colormod,0)
        elif volt <= 120:
            colormod = min(((120-volt) * 65535/30), 65535)
            color = (0, 65535-colormod, colormod)

        button = self.ui.get("volt_cm730")
        gtkColor = gtk.gdk.Color(*color)
        button.modify_bg(gtk.STATE_NORMAL, gtkColor) 
        button.modify_bg(gtk.STATE_ACTIVE, gtkColor) 
        button.modify_bg(gtk.STATE_PRELIGHT, gtkColor) 
        button.modify_bg(gtk.STATE_SELECTED, gtkColor)

        label = "CM_730\n" + str(volt)
        button.set_label(label)
    
    def update_max_volt(self,item):
        """Display the current max voltage we get as a message
        """
        if item is None or item.type != "number":
            return
        lable = self.ui.get("maxVolt")
        volts = item.value/10.0
        lable.set_text(str(volts))

    def update_min_volt(self,item):
        """Display the current min voltage we get as a message
        """
        if item is None or item.type != "number":
            return
        label = self.ui.get("minVolt")
        volts = item.value/10.0
        label.set_text(str(volts))

    def update_max_temp(self,item):
        """Display the current maximum temperature we receive as a message
        """
        if item is None or item.type != "number":
            return
        label = self.ui.get("maxTemp")
        label.set_text(str(item.value))

    def update_max_temp_origin(self,item):
        """Display Motor responsible for max-temp
        """
        if item is None or item.type != "number":
            return
        label = self.ui.get("maxTempOrigin")
        label.set_text("(Motor " +str(item.value)+")")
        
    def update_goal(self,item):
        """Show the current goal
        """
        if item is None or item.type != "string":
            return
        goal = item.value
        label = self.ui.get("currentGoal")
        if goal == "blue":
            label.set_markup("<span foreground='blue'>blue</span>")
        else:
            label.set_markup("<span foreground='yellow'>yellow</span>")

    def update_motor_error(self,item):
        """Update the Error view to show the last received Error
        """
        if item is None or item.type != "number" or item.value not in range(1,21):
            return
        motor_id = item.value
        for dxi in range(1,21):
            motor = self.ui.get("err_motor%d" % dxi)
            
            #darken old colors with each new error
            colors =[]
            for color in motor.get_style().bg :
                h = color.hue
                s = color.saturation
                v = color.value
                v *= 0.5
                colors.append(gtk.gdk.color_from_hsv(h,s,v))
            motor.modify_bg(gtk.STATE_NORMAL, colors[0]) 
            motor.modify_bg(gtk.STATE_ACTIVE, colors[1]) 
            motor.modify_bg(gtk.STATE_PRELIGHT, colors[2]) 
            motor.modify_bg(gtk.STATE_SELECTED, colors[3])

        #set motor of the newly received error to be red
        motor = self.ui.get("err_motor%d" %motor_id)
        color = gtk.gdk.color_parse("#FF0000")
        motor.modify_bg(gtk.STATE_NORMAL, color) 
        motor.modify_bg(gtk.STATE_ACTIVE, color) 
        motor.modify_bg(gtk.STATE_PRELIGHT, color) 
        motor.modify_bg(gtk.STATE_SELECTED, color)

    def update_motor_error_id(self,item):
        """Display the kind of error we received last
        """
        if item is None or item.type != "number":
            return
        message = error_ids[item.value]
        label = self.ui.get("lastError")
        label.set_markup("<span foreground='red'>%s</span>"%message)

    def cleanup(self):
        self.ui.window.destroy()
