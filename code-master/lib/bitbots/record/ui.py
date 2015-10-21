#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
UI Classes and Functions.
^^^^^^^^^^^^^^^^^^^^^^^^^

The UI utilizes `urwid <http://excess.org/urwid/docs/index.html>`_ as a library for console guis.
I strongly recommend reading the official documentation if you plan any bigger changes on this
module.

.. moduleauthor:: Timon Giese <timon.giese@bit-bots.de>

"""
import logging
import signal

import urwid  # Library for console UI's
import urwid.raw_display
import urwid.curses_display
import yaml  # Library for certain structured data files

from bitbots.ipc import SharedMemoryIPC
from bitbots.util import get_config, find_resource
from bitbots.record.help_parser import HelpParser
from bitbots.record.record import Recorder
from bitbots.record.util import JsonConverter, MotorInfoProvider
from bitbots.record.handler import DarwinDebugHandler
from bitbots.record.widget import DataFieldWidget, ScrollIndicatorWidget, KeyframeWidget, ConsoleWidget, MetaViewWidget, MotorViewWidget

#get config
config = get_config()['Record']

# Start Logging Tools
# The Internal logger "ilog" is very important,
# because it handles user-Output as well
# The Handler for that is added by the ConsoleWidget
ilog = logging.getLogger('record-gui')  # internal logger
ilog.setLevel(config['log_level_global'])
# Standard FileHandler for easy output in a file (optional)
if config['log_file'] is not None and len(config['log_file']) > 0:
    ilog.addHandler(logging.FileHandler(config['log_file']))
# DarwinDebugHandler sendet Debug-Daten an das normale Darwin-Logging
ext = DarwinDebugHandler()
ext.setLevel(config['darwin_debug_level'])
ilog.addHandler(ext)


class HelpView(urwid.Frame):
    def __init__(self):
        self.load_help()
        self.ftext = urwid.Text("Dummy")
        self.filler = urwid.Filler(self.ftext)
        self.parser = HelpParser(logger=ilog)
        return super(HelpView, self).__init__(self.filler, urwid.Text("Hilfe-Ansicht"))

    def load_help(self):
        """ Parse the yaml-file with the help information
        """
        try:
            path = find_resource('record_help.yaml')
            with open(path, 'r') as f:
                self.helpmap = yaml.load(f)
                ilog.debug('help-file successfully loaded')
        except IOError:
            ilog.warn('help-file could not be opened! - no help availiable')
            self.helpmap = None
        except yaml.YAMLError as e:
            ilog.warn('help-file could not be parsed! - no help availiable')
            ilog.warn("Error in help-file: %s" % e)

    def show_topic(self, arguments):
        text = []
        arg0 = arguments[0]
        if not self.helpmap:
            ilog.warn("Help not avaliable (look for previous errors)")
            return False
        if not arguments[0] in self.helpmap:
            ilog.info("Help on the topic %s could not be found" % arg0)
            return False
        topic = self.helpmap
        while arguments:
            arg = arguments.pop()
            if not arg in topic:
                ilog.info("Help on the subtopic %s could not be found." % arg)
                return False
            topic = topic[arg]
        if 'usage' in topic:
            text.append(('help_usage', topic['usage'] + '\n\n'))
        ilog.debug("Calling Parser for topic %s" % arg0)
        text.extend(self.parser.parse(topic['help']))
        self.ftext.set_text(text)
        return True


class Mainframe(urwid.Frame):
    """ The top-level container for the GUI. Essentially the GUI itself.
    :param size: Irrellevant for us
    :param key: pressed key (bytes or unicode string)
    """

    def __init__(self, ui_debug=False, ipc=None):
        #init logging

        # Palette maps colors to attribute specifiers
        # All UI-Elements may be assigned these attributes
        palette = self.load_palette()
        # Set Encoding to UTF-8
        # usually urwid respects the system locale
        # but it is much more likely that the locale is wrong,
        # than that we ever need other encodings than utf-8.
        urwid.set_encoding("UTF-8")
        # register signals
        urwid.register_signal(DataFieldWidget, ['field_changed'])
        urwid.register_signal(KeyframeWidget, ['frame_changed'])
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        signal.signal(signal.SIGINT, self.handle_sigint)

        # Set to true when a shutdown was sheduled
        # Set to false when a sheduled shutdown shall be aborted
        self.shutdown_sheduled = False

        # init ipc if not given
        if not ipc:
            ipc = SharedMemoryIPC()

        self.rec = Recorder(ipc, self, ilog)

        self.converter = JsonConverter()

        #Define the ListWalker for the list of FrameElements
        self.listWalker = urwid.SimpleListWalker([])
        self.keyframelist = urwid.ListBox(self.listWalker)
        #Header of the UI-Frame (stays on top)
        self.headline = "Record Script - Exit:<q> Leave ConsoleWidget:<ESC> Use ConsoleWidget:<:>"
        self.header = urwid.Text(('caption3', self.headline))
        #Footer of the UI-Frame (stays on bottom, contains the console)
        loglevel = config['console_log_level']
        self.console = ConsoleWidget(ipc, self.rec, self, loglevel)

        # HelpView
        self.helpView = HelpView()

        # Motor View
        self.motorView = MotorViewWidget()

        # Motor Info View
        self.motorInfoProvider = MotorInfoProvider()
        self.motorInfoLW = urwid.SimpleListWalker([])
        self.motorInfos = urwid.ListBox(self.motorInfoLW)
        self.motorInfoList = ScrollIndicatorWidget(self.motorInfos)

        # Frame View
        self.frameList = ScrollIndicatorWidget(self.keyframelist)

        #Initialise the Mainframe
        super(Mainframe, self).__init__(self.frameList,
                                        self.header, self.console)
        self.update_meta()

        # Select the Screen Type ('curses' or the default 'raw')
        if 'screen' in config and config['screen'] == 'curses':
            screen = urwid.curses_display.Screen()
        else:
            screen = urwid.raw_display.Screen()
            screen.set_terminal_properties(colors=256, bright_is_bold=False, has_underline=True)

        #Start the UI-Loop
        self.loop = urwid.MainLoop(
            self, palette, unhandled_input=self.unhandled_input, screen=screen)
        self.set_focus('footer')
        with ipc.record:
            if not ui_debug:
                self.loop.run()

    def unhandled_input(self, key):
        """ Input accepted by no UI-Element ends up here.
        """
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 'm':
            if self.contents['body'] == (self.frameList, None):
                self.display_motor_ids()
            else:
                self.display_frames()
        elif key == 'M':
            if isinstance(self.contents['body'][0], MetaViewWidget):
                self.display_frames()
            else:
                self.display_meta()
        elif key == 'g':
            self.frameList.go_top()
        elif key == 'G':
            self.frameList.go_bottom()
        elif key == ':':
            self.focus_position = 'footer'
        elif key == 'esc':
            self.focus_position = 'body'
        elif key == 'f12':
            self.reload_ipc()

    def reload_ipc(self):
        """
        Tries to reload the IPC
        """
        ipc = SharedMemoryIPC()
        self.rec.set_ipc(ipc)
        self.console.set_ipc(ipc)


    def __setattr__(self, name, value):
        """ Listen to some attribute-changes
        We hack in to urwid to check when the Focus changes
        """
        # Increase Consol-Size on focus
        if name is 'focus_part':
            ilog.debug("Changing Main-Focus")
            body = self.contents['body'][0]
            if value is 'footer':
                if isinstance(body, MetaViewWidget):
                    ilog.debug("Leaving Meta-View, better save it.")
                    body.save()
                self.console.expand()
                self.contents['body'] = (self.frameList, None)
            else:
                self.console.minimize()
        super(Mainframe, self).__setattr__(name, value)

    def append_keyframe(self, frame):
        """ Add a new keyframe to the UI.
        Called by the recorder to update the UI after a "record" command
        """

        # The converter gives back a nicer representation of the keyframe for
        # our purpose.
        values = self.converter.get_keyframe_data(frame)

        # A bit of error handling
        if not values:
            ilog.warning("Keyframe not loaded, because of previous error")
            return False

        # Determine new "current" keyframe-number
        current = len(self.listWalker) + 1

        # Make us a shiny new UI-element for this keyframe
        fe = KeyframeWidget(current, values)
        # Listen to Events by this UI-element
        urwid.connect_signal(fe, 'frame_changed', self.on_frame_change)
        # Attach it to our ListViewWidget (by handing it to the walker)
        self.listWalker.append(fe)
        # Make sure the user can look at his new keyframe without additional
        # keypresses
        self.frameList.go_bottom()

        return True

    def pop_keyframe(self, framenumber=-1):
        """ Remove a Keyframe from the Keyframelist

        :param framenumber: the number of the frame to pop (0 == first element)
        """
        return self.listWalker.pop(framenumber)

    def update_meta(self):
        """ Update the Meta information in the header
        """
        meta = "name: %s | version: %s | last edited: %s" % (
            self.rec.name, self.rec.version, self.rec.last_edited)
        self.header = urwid.Text([
            ('caption3', self.headline + '\n'),
            ('caption2', meta)])

    def display_keyframes(self, anim):
        """ display a new animation replacing the old one.

        :param anim: new animation in original dict representation (like in the file)
        """
        del self.listWalker[:]
        for frame in anim:
            if not self.append_keyframe(frame):
                # If an error occured while loading the keyframe for the UI
                # The Recorder itself SHOULD notice our negative feedback
                # however if it won't, this might induce problems.
                ilog.error("The new animation made me sick... check for unexpected behaviour")
                del self.listWalker[:]
                return False
        self.update_meta()
        self.display_frames()

    def write_frame(self, frame, field):
        """ write frame back to the recorder, if it was changed in the gui.
        """
        index = frame.framenumber - 1
        frame = self.listWalker[index]
        keyframedata = frame.get_data()
        anim = self.converter.get_dict(keyframedata)
        self.rec.save_step("Changed Keyframe %03d, Field %s to value %s" % (frame.framenumber, field.title_text, field.edit_text))
        self.rec.anim[index] = anim

    def is_valid(self):
        if len(self.listWalker) is 0:
            return False
        for keyframe in self.listWalker:
            if not keyframe.valid:
                return False
            if __debug__:
                ilog.debug('Keyframe %i is valid' % keyframe.framenumber)
        return True

    def on_frame_change(self, frame, field):
        if frame.valid:
            self.write_frame(frame, field)
            if __debug__:
                ilog.debug('Frame %03d updated because field %s was changed' % (frame.framenumber, field.title_text))
        ilog.debug("Redrawing Screen after Frame-change")

        # Having update-issues when the frame-title is changed
        # Calling draw_screen right away (as documented) will not help
        # I spent two days trying to figure out the reason for
        # this behaviour, found nothing and ended up using this:
        def call_draw(loop, user_data):
            loop.draw_screen()
        self.loop.set_alarm_in(0.01, call_draw)

    def display_motor_ids(self, group=None):
        #self.contents['body'] = (urwid.Filler(urwid.Text(
        #    motorIdsFormated)), None)
        success = True
        if group:
            success = self.motorView.highlight(group)
        self.contents['body'] = (self.motorView, None)
        self.focus_position = 'body'
        return success

    def display_help(self, topic):
        """ Shows help to topic
        :param list topic: help arguments
        """
        if self.helpView.show_topic(topic):
            self.contents['body'] = (self.helpView, None)
            return True
        return False

    def display_meta(self):
        self.contents['body'] = (MetaViewWidget(self, self.rec), None)
        self.focus_position = 'body'

    def display_frames(self):
            self.contents['body'] = (self.frameList, None)

    def display_motor_info(self, arg=None):
        infos = self.motorInfoProvider.get_motor_info(arg)
        if infos:
            del self.motorInfoLW[:]
            for widget in infos:
                self.motorInfoLW.append(widget)
            self.contents['body'] = (self.motorInfoList, None)
            return True
        return False

    def load_palette(self):
        """ Identifys the Theme requested by the user and tries to load it
        """

        def obtain_palette(theme):
            """ Makes the I/O to load a theme
            """
            try:
                path = find_resource('record_themes/' + theme)
                ilog.info("record color specification located as: %s" % path)
                with open(path, 'r') as f:
                    palette = yaml.load(f)
                    ilog.debug('colors successfully loaded')
                    return palette
            except IOError:
                ilog.warn('color-file could not be opened!')
                self.helpmap = None
            except yaml.YAMLError as e:
                ilog.warn('color-file could not be parsed!')
                ilog.warn("Error in color-file: %s" % e)
            return []

        palette = []

        if 'theme' in config:
            theme = config['theme']
            ilog.debug('Using Theme %s' % theme)
            if not theme.endswith('.yaml'):
                theme += '.yaml'
        else:
            theme = 'default.yaml'
            ilog.debug('No Theme specified in the config - using default')
        palette = obtain_palette(theme)
        if not palette and not theme == 'default.yaml':
            ilog.warning("Could not load theme %s, trying default-theme instead!" % theme)
            palette = obtain_palette('default.yaml')

        return palette

    def handle_sigterm(self, signal, frame):
        """ Reacts on System-Termination
        by saving.
        """
        ilog.warning("Received Termination-Signal by system!")
        ilog.info("Trying to rescue Animation...")
        self.rec.dump('terminated', force=True)
        ilog.warning("Exiting... press ANY KEY to abort!")
        self.shutdown_sheduled = True

        # we are outside of the urwid-loop, so we have to refresh manually:
        self.loop.draw_screen()

        # shedule shutdown
        self.loop.set_alarm_in(5, self.exit_when_no_reaction)

    def handle_sigint(self, signal, frame):
        ilog.warning(
            "Received SIGINT, but I have no way to handle this right now.")

    def exit_when_no_reaction(self, mainloop, user_data):
        if self.shutdown_sheduled:
            print "Exiting as a result of a SIGTERM, Good Bye"
            raise urwid.ExitMainLoop()
        else:
            ilog.debug("Sheduled Shutdown should be executed now, but it was abortet")

    def keypress(self, size, key):
        """ Handle Keypresses, before
        we let our children get them.
        """

        # abort shutdown
        if self.shutdown_sheduled:
            self.shutdown_sheduled = False
            ilog.info("Shutdown aborted.")
            return
        return super(Mainframe, self).keypress(size, key)
