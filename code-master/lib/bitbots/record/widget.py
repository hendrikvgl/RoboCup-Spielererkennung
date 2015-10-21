#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
Urwid-Widgets für das Record-UI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Timon Giese <timon.giese@bit-bots.de>

History:
--------

    * 2014-06-30: Feature: p-gain unterstützung (p drücken bei selektiertem keyframe)
    * 2014-01-17: Modul angelegt, Klassen aus der ui.py gezogen, wo nur das
      Hauptfenster verbleiben soll.

"""
import logging
import urwid
#Start Logging Tools
ilog = logging.getLogger('record-gui')  # internal logger
from bitbots.record.record import JointManager
from bitbots.util import Joints
from bitbots.record.commands import Commander
from bitbots.record.handler import ConsoleHandler
from bitbots.util.ascii import motorIdsFormated
from bitbots.robot.pypose import num_pose_joints

PAU_MAX_VAL = 999
PAU_MIN_VAL = 0
DUR_MAX_VAL = 999
DUR_MIN_VAL = 0


class FocusWatchMixin(object):
    def __init__(self, *args, **kwargs):
        self.last_focus = False
        retval = super(FocusWatchMixin, self).__init__(*args, **kwargs)
        urwid.register_signal(self.__class__, ['focus_won', 'focus_lost', 'field_changed'])
        return retval

    def render(self, size, focus=False):
        if focus and not self.last_focus:
            urwid.emit_signal(self, 'focus_won')
        if not focus and self.last_focus:
            urwid.emit_signal(self, 'focus_lost')
        self.last_focus = focus
        return super(FocusWatchMixin, self).render(size, focus=focus)


class DataFieldWidget(FocusWatchMixin, urwid.Edit):
    """ Single UI Element representing a Motor or DUR / PAU values"""

    def _get_title_text(self):
        """ Orignal Caption Text component
        """
        return self.orig_caption[1]

    title_text = property(_get_title_text)

    def __init__(self, value, limit_high=180, limit_low=-180):
        self.value = value
        self.limit_high = limit_high
        self.limit_low = limit_low

        def check_attr(attr):
            if not hasattr(self, attr):
                ilog.error('DataFieldWidget is missing the attribute %s' +
                           'which should be set by a subclass!' % attr)
                raise NotImplementedError

        check_attr('allowed_chars')
        check_attr('orig_caption')

        text = "%s" % value  # value will be verified in check_content below

        super(DataFieldWidget, self).__init__(self.orig_caption,
                                              align='center',
                                              edit_text=text)

        urwid.connect_signal(self, 'focus_lost', self.check_content)
        self.check_content()  # initially check own content

    def keypress(self, size, key):
        """ Keyboard Input for this urwid Widget
        see `Urwid.Widget.keypress\
        <http://excess.org/urwid/docs/reference/widget.html#urwid.Widget.keypress>`_

        :param size: Irrellevant for us
        :param key: pressed key (bytes or unicode string)

        """
        if key == 'delete':
            self.set_edit_text("")
            return
        elif key == 'enter':
            self.check_content()
            return
        return super(DataFieldWidget, self).keypress(size, key)

    def valid_char(self, ch):
        """ Allowed characters in the edit-text.
        further restrictions are implemented in the override method
        :py:func:`set_edit_text`.
        """
        return ch in self.allowed_chars

    def limit(self, value):
        """Puts an value into the allowed range
        :param float value: value to check
        """
        if value < self.limit_low:
            ilog.debug('Field input increased to low limit')
            return self.limit_low
        if value > self.limit_high:
            ilog.debug('Field input reduced to high limit')
            return self.limit_high
        return value

    def set_edit_text(self, text):
        """ Checks for correctness of input before passing to superclass
        """
        # allow to empty the Box
        if len(text) == 0:
            super(DataFieldWidget, self).set_edit_text(text)
            if __debug__:
                ilog.debug('empty field')
            return True
        # set ignore attribute
        if text == 'i':
            super(DataFieldWidget, self).set_edit_text("IGNORE")
            if __debug__:
                ilog.debug('single i inputted')
            return True

        # check if input is a float (or a single '-')
        # and if it is in the allowed range
        if not text in ['-', 'IGNORE']:
            val = "none"
            try:
                val = float(text)
                val = int(text)
            except ValueError:
                if isinstance(val, str):
                    ilog.debug("Illegal field value: %s !" % text)
                    return False
            text = str(self.limit(val))

        # let the superclass do the rest
        if __debug__:
            ilog.debug("field input ok")
        self.caption_unsaved()
        self.unsaved = True
        super(DataFieldWidget, self).set_edit_text(text)

    def format_content(self):
        """ Format the content of the edit-field into a unified representation
        """
        text = "%0.3f" % float(self.edit_text)
        super(DataFieldWidget, self).set_edit_text(text)

    def check_content(self):
        """ Display invalid values
        If the content is not in the allowed range of values
        for this motor, the header is set to an alert-color
        If everything is fine (again?) (re-)set header to normal color
        """
        try:
            float(self.edit_text)
            self.caption_normal()
            self.format_content()
            self.valid = True
            urwid.emit_signal(self, 'field_changed', self)
            return True
        except ValueError:
            ilog.debug("Field content %s invalid" % self.edit_text)
            self.caption_alert()
            self.valid = False
            urwid.emit_signal(self, 'field_changed', self)
            return False

    def caption_alert(self):
        """ Set this Field-Caption to the alert-color
        """
        self.set_caption(('alert', self.title_text))

    def caption_unsaved(self):
        """ Set this Field-Caption to the unsaved-color
        """
        self.set_caption(('unsaved', self.title_text))

    def caption_normal(self):
        """ Set this Field-Caption to the standard-color
        """
        #use special color for PAU and DUR:
        self.set_caption(self.orig_caption)


class PauseFieldWidget(DataFieldWidget):
    """ A :py:class:`DataFieldWidget` displaying pause-values
    """

    def __init__(self, value):
        self.orig_caption = ('caption2', "PAU:\n")
        self.allowed_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
        return super(PauseFieldWidget, self).__init__(value, limit_high=999, limit_low=0)


class DurationFieldWidget(DataFieldWidget):
    """ A :py:class:`DataFieldWidget` displaying duration-values
    """

    def __init__(self, value):
        self.orig_caption = ('caption2', "DUR\n")
        self.allowed_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
        return super(DurationFieldWidget, self).__init__(value, limit_high=999, limit_low=0)


class MotorFieldWidget(DataFieldWidget):
    """ A :py:class:`DataFieldWidget` displaying motor-position-values
    """
    def __init__(self, number, value):
        self.orig_caption = ('caption1', "#%i\n" % number)
        self.number = number
        self.allowed_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '-', 'i']
        return super(MotorFieldWidget, self).__init__(value)

    def check_content(self):
        if self.edit_text == "IGNORE":
            self.caption_normal()
            self.valid = True
            urwid.emit_signal(self, 'field_changed', self)
            return True
        else:
            return super(MotorFieldWidget, self).check_content()


class GainFieldWidget(DataFieldWidget):
    """ A :py:class:`DataFieldWidget` displaying motor-gain-values
    """
    def __init__(self, number, value):
            self.orig_caption = ('caption1', "p%i\n" % number)
            self.allowed_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'i']
            super(GainFieldWidget, self).__init__(value, limit_high=255, limit_low=0)

    def format_content(self):
        """ Format the content of the edit-field into a unified representation
        """
        text = "%i" % int(self.edit_text)
        super(GainFieldWidget, self).set_edit_text(text)

    def check_content(self):
        if self.edit_text == "IGNORE":
            self.caption_normal()
            self.valid = True
            urwid.emit_signal(self, 'field_changed', self)
            return True
        else:
            try:
                i = int(self.edit_text)
                if not 0 <= i <= 255:
                    ilog.debug("Gain invalid, because it is not in the range (0,256)")
                    self.valid = False
                    self.caption_alert()
                    return False
                else:
                    self.valid = True
                    self.caption_normal()
                    return True
            except ValueError:
                ilog.debug("Gain invalid, because it is not an integer")
                self.valid = False
                self.caption_alert()
                return False
            finally:
                urwid.emit_signal(self, 'field_changed', self)


class ScrollIndicatorWidget(urwid.Frame):
    """Container for the Keyframe-list.
    Will display ▲ or ▼ in the header/footer area to mark
    when the List does not fit in the view-area and has to be
    scrolled.
    """
    def __init__(self, list_box):
        self.list_box = list_box
        super(ScrollIndicatorWidget, self).__init__(self.list_box)

    def render(self, size, focus=False):
        """ Kind of a hack, due to shortcommings of urwid.
        """
        visible = self.list_box.ends_visible(size, focus)
        if 'top' in visible:
            if not self.list_box.body:
                header = """
__________________________________________   ╭--╮
| Wie es aussieht versuchen Sie gerade     \ (●)(●)
 | eine Animationsdatei aufzunehmen.         \ |╷ | /
| Darf ich Ihnen dabei behilflich sein?      \|| ||
| Tippen Sie einfach "help" in die Console.  /|╰-╯|
 ___________________________________________/ ╰---╯
 """
                self.header = urwid.Text(('warning', header), align='center')
            else:
                self.header = None
        else:
            self.header = urwid.AttrMap(
                urwid.Divider(u'▲'), {None: 'scroll_indicator'})
        if 'bottom' in visible:
            self.footer = None
        else:
            self.footer = urwid.AttrMap(
                urwid.Divider(u'▼'), {None: 'scroll_indicator'})

        return super(ScrollIndicatorWidget, self).render(size, focus)

    def go_top(self):
        """Moves Focus in the KeyframeList to the first item
        """
        if self.list_box.body.contents:
            self.list_box.body.set_focus(0)

    def go_bottom(self):
        """Moves Focus in the KeyframeList to the last item
        (happens when appending frames too)
        """
        if self.list_box.body.contents:
            i = len(self.list_box.body) - 1
            self.list_box.body.set_focus(i)


class KeyframeWidget(urwid.LineBox):
    """ Single UI-Element to display all properties of a Keyframe
    Top-Level container is an urwid LineBox, containing a GridFlow layout
    The Grid-Flow contains LineBoxed MotorElements (which extend Edit Fields)
    """

    def __init__(self, framenumber, anim):
        self.data_fields = []
        self.gain_fields = []
        self.data_boxes = []
        self.gain_boxes = []
        self.framenumber = framenumber
        self.valid = True

        goals = anim['goals']
        gains = anim['gains']
        assert len(goals) is (num_pose_joints())
        assert len(gains) is (num_pose_joints())

        for i in range(num_pose_joints()):
            motor_field = MotorFieldWidget(i + 1, goals[i])
            urwid.connect_signal(
                motor_field, 'field_changed', self.field_changed)
            self.data_fields.append(motor_field)
            mapped = urwid.AttrMap(urwid.LineBox(motor_field), 'data_field_outline', focus_map='data_field_outline_focus')
            self.data_boxes.append(mapped)

            gain_field = GainFieldWidget(i + 1, gains[i])
            urwid.connect_signal(
                gain_field, 'field_changed', self.field_changed)
            self.gain_fields.append(gain_field)
            mapped = urwid.AttrMap(urwid.LineBox(gain_field), 'data_field_outline', focus_map='data_field_outline_focus')
            self.gain_boxes.append(mapped)
        duration_field = DurationFieldWidget(anim['duration'])
        urwid.connect_signal(
            duration_field, 'field_changed', self.field_changed)
        pause_field = PauseFieldWidget(anim['pause'])
        urwid.connect_signal(pause_field, 'field_changed', self.field_changed)
        self.data_fields.append(duration_field)
        self.data_fields.append(pause_field)
        mapped = urwid.AttrMap(urwid.LineBox(duration_field), 'data_field_outline', focus_map='data_field_outline_focus')
        self.data_boxes.append(mapped)
        mapped = urwid.AttrMap(urwid.LineBox(pause_field), 'data_field_outline', focus_map='data_field_outline_focus')
        self.data_boxes.append(mapped)

        self.data_gridFlow = urwid.GridFlow(self.data_boxes, 10, 0, 0, 'left')
        self.gain_gridFlow = urwid.GridFlow(self.gain_boxes, 10, 0, 0, 'left')
        self.displaying_p = False
        super(KeyframeWidget, self).__init__(self.data_gridFlow,
                                             "Frame %03d" % framenumber)

    def keypress(self, size, key):
        """ Keyboard Input for this urwid Widget
        see `Urwid.Widget.keypress\
        <http://excess.org/urwid/docs/reference/widget.html#urwid.Widget.keypress>`_

        :param size: Irrellevant for us
        :param key: pressed key (bytes or unicode string)

        .. hint::

            Keypresses not catched here are passed to all children.
            If they come back they may be handled here.
            If this class is not responsible for the keypresses at all,
            we return them back to our caller.
        """
        # catch input before we pass it to children:
        #vim-like movements:
        if key == 'k':
            return super(KeyframeWidget, self).keypress(size, 'up')
        elif key == 'j':
            return super(KeyframeWidget, self).keypress(size, 'down')
        elif key == 'l':
            return super(KeyframeWidget, self).keypress(size, 'right')
        elif key == 'h':
            return super(KeyframeWidget, self).keypress(size, 'left')
        elif key == 'n':
            return 'down'
        elif key == 'p':
            self.toggle_gain()
        #pass other input to the superclass
        else:
            key = super(KeyframeWidget, self).keypress(size, key)
            #non-handled keys come back to us now

        # change focus on TAB
        if key == 'tab':
            #erst ab späteren urwid versionen, aber eleganter:
            try:
                self.data_gridFlow.focus_position += 1
            except IndexError:
                self.data_gridFlow.focus_position = 0
        return key

    def toggle_gain(self):
        """ Toggles display of gain-values vs. "normal" keyframe-data.

        This method uses an ugly *hack* to exchange the content of this widget.
        The Library does not provide a method to change the content of a decoration
        widget. However historically it was decided to make this class an extension of
        a LineBox decoration widget and we are not going to change that at this point.

        To change the content of our widget nevertheless, we call the superclass constructor
        _again_ with new content. That should be somewhat safe to do (checked the library source).
        Afterwards we make a call to the private method self._invalidate() in order to avoid
        assured mayhem and destruction.
        """
        # get_text returns a 2-Tuple. First component is the text, second a _internal_ markup
        # I would love to be able to just pass the tuple as "markup" to set_text
        # but oddly the ouput from get_text is not compatible to set_text
        # (you can blame urwid for that one #FIXOTHER)
        oldtitle = self.title_widget.get_text()[0]
        if not self.displaying_p:
            super(KeyframeWidget, self).__init__(self.gain_gridFlow,
                                                 "Frame %03d" % self.framenumber)
            self.displaying_p = True
        else:
            super(KeyframeWidget, self).__init__(self.data_gridFlow,
                                                 "Frame %03d" % self.framenumber)
            self.displaying_p = False
        if self.valid:
            self.title_widget.set_text(oldtitle)
        else:
            self.title_widget.set_text(('alert', oldtitle))
        self._invalidate()

    def check_valid(self):
        for field in (self.data_fields + self.gain_fields):
            if not field.valid:
                self.valid = False
                ilog.debug('Frame %03d is invalid' % self.framenumber)
                return False
        self.valid = True
        return True

    def title_normal(self):
        self.title_widget.set_text(" Frame %03d " % self.framenumber)
        self.tline_widget._invalidate()
        self._invalidate()

    def title_alert(self):
        self.title_widget.set_text(('alert', " Error in Frame %03d " % self.framenumber))
        self.tline_widget._invalidate()
        self._invalidate()

    def field_changed(self, field):
        """ Called when an Field within this Keyframe was changed.
        Performs a check for validity of the components and displays
        the Framenumber in an alert color if the Keyframe contains errors.
        """
        if field.valid and not self.valid:
            if self.check_valid():  # perform only on success
                self.valid = True
                ilog.debug("setting default color in Frame %03d " % self.framenumber)
                self.title_normal()
        elif not field.valid and self.valid:
            self.valid = False
            ilog.debug("setting alert color in Frame %03d " % self.framenumber)
            self.title_alert()
        urwid.emit_signal(self, 'frame_changed', self, field)

    def get_data(self):
        """ Data for :py:func:`bitbots.record.util.JsonConverter.get_dict`

        :return: Field Data
        :rtype: List of Strings
        """
        data = {'goals': []}
        for elem in self.data_fields[:-2]:
            data['goals'].append(elem.edit_text)
        data['gains'] = []
        for elem in self.gain_fields:
            data['gains'].append(elem.edit_text)
        data['duration'] = self.data_fields[-2].edit_text
        data['pause'] = self.data_fields[-1].edit_text
        return data


class ConsoleWidget(urwid.BoxAdapter):
    """ User In-/Output
    Receives all debug-messages of Informational and above as output

    :param ipc: Shared Memory IPC
    :param recorder: recorder instance (will be passed to the commander)
    :param gui: Mainframe-Instance
    :param loglevel: Loglevel of the ConsoleWidget output (default logging.INFO)
    """
    def __init__(self, ipc, recorder, gui, loglevel=logging.INFO):
        self.edit = urwid.Edit(('command_indicator', ">_ "))
        self.history_listWalker = urwid.SimpleListWalker([])
        self.history_ui = urwid.ListBox(self.history_listWalker)
        self.command_history = []
        self.command_history_pos = 0
        self.frame = urwid.Frame(
            self.history_ui, urwid.Divider('='), self.edit)
        self.frame.focus_position = 'footer'
        self.ipc = ipc
        self.gui = gui
        self.handler = ConsoleHandler(self)
        self.handler.setLevel(loglevel)
        ilog.addHandler(self.handler)
        jm = JointManager(ipc)
        self.commander = Commander(
            c_handler=self.handler, recorder=recorder, jm=jm, ui=gui)
        super(ConsoleWidget, self).__init__(self.frame, 8)

    def set_ipc(self, ipc):
        self.ipc = ipc
        self.commander.set_jm_ipc(ipc)

    def autocomplete(self):
        """ Extends input command if possible
        Usually called after User presses <Tab>
        """
        # First decompose the contents of the input
        line = self.edit.edit_text.strip().split()
        ilog.debug("calling autocomplete for %s" % line)

        # No input, no autocomplete
        if not line:
            ilog.debug("Nothing to autocomplete, aborting")
            return False

        possible = self.commander.autocomplete(line[0], line[1:])

        # No completions found, well bad luck.
        if not possible:
            ilog.info("no completions found")
            return False

        # exactly one possible completion, we just do it without nagging around
        if len(possible) == 1:
            text = ""
            line[-1] = possible[0]
            for word in line:
                text += word + " "
            self.edit.set_edit_text(text)
            self.edit.set_edit_pos(len(self.edit.edit_text))
            return True

        # multiple extensions
        # We try to complete the part that is unambigous
        else:
            abort = False
            pre = ""
            new_pre = ""
            i = 0
            while not abort:
                for poss in possible:
                    if not poss.startswith(new_pre):
                        abort = True
                        continue

                # prepare next run
                if not abort:
                    pre = new_pre
                    try:
                        new_pre = pre + possible[0][i]
                        i += 1
                    # abort if the first word in the possible list is too short
                    # to complete
                    except IndexError:
                        abort = True

            # Set Edit-Field to new result
            text = ""
            line[-1] = pre
            for word in line[:-1]:
                text += word + " "
            text += line[-1]
            self.edit.set_edit_text(text)
            self.edit.set_edit_pos(len(self.edit.edit_text))

        # If we have less than 20 Possibilities we print them out for
        # convenience
        if len(possible) < 20:
            text = "Possible Completions: "
            for poss in possible:
                text += poss + " "
            ilog.info(text)

        # If we have more, we just tell the user
        else:
            ilog.info("I have many possibilities to complete this...")

    def process_input(self):
        """ Triggered when input is sent (return)

        * checks input
        * calls command routines
        * updates history
        * clears edit field
        """

        line = self.edit.edit_text.strip().split()
        if not line:
            return
        command = line[0]
        arguments = line[1:]
        text = self.edit.get_edit_text()
        self.command_history.append(text)
        if self.commander.has_command(command):
            text = ">_ " + text
            ilog.info(text)
            try:
                self.commander.run(command, arguments)
            except urwid.ExitMainLoop:
                raise
            except Exception as e:
                import traceback
                traceback = traceback.format_exc()
                ilog.error(u"Error: %s \n %s" % (str(e), traceback))
        else:
            ilog.error("Fehler, unbekannter Befehl %s" % command)
        self.edit.set_edit_text('')
        self.command_history_pos = len(self.command_history)

    def com_history_up(self):
        """ Moves backwards in the command history.

        Sets the command-line content accordingly
        """
        ilog.debug("history up (bachwards)")
        pos = self.command_history_pos - 1
        if pos >= 0:
            try:
                self.edit.set_edit_text(self.command_history[pos])
                self.edit.edit_pos = len(self.edit.edit_text)
                self.command_history_pos = pos
            except IndexError:
                ilog.error("Something went unexpectedly wrong in the command-history, I am resetting it.")
                self.command_history_pos = len(self.command_history)
        else:
            ilog.warn('End of Command history reached')

    def com_history_down(self):
        """ Moves forward in the command history.

        Sets the command-line content accordingly
        """
        ilog.debug("history down (forwards)")
        pos = self.command_history_pos + 1
        try:
            self.edit.set_edit_text(self.command_history[pos])
            self.edit.set_edit_pos(len(self.edit.edit_text))
        except IndexError:
            ilog.debug("commandline-history cannot forsee the future (yet)")
            self.edit.set_edit_text('')
            self.edit.set_edit_pos(0)
            self.command_history_pos = len(self.command_history)
            return False
        self.command_history_pos = pos
        return True

    def keypress(self, size, key):
        """ Keyboard Input for this urwid Widget
        see `Urwid.Widget.keypress\
        <http://excess.org/urwid/docs/reference/widget.html#urwid.Widget.keypress>`_

        :param size: Irrellevant for us
        :param key: pressed key (bytes or unicode string)

        .. hint::

            Keypresses not catched here are passed to all children.
            If they come back they may be handled here.
            If this class is not responsible for the keypresses at all,
            we return them back to our caller.
        """
        if key == 'enter':
            self.process_input()
        elif key == 'up':
            if self.frame.focus_position == 'footer':
                self.com_history_up()
                return
        elif key == 'down':
            if self.frame.focus_position == 'footer':
                self.com_history_down()
                return
        elif key == 'tab':
            self.autocomplete()
            return
        elif key == 'shift up':
            self.frame.focus_position = 'body'
        elif key == 'shift down':
            self.frame.focus_position = 'footer'
        #Return ESC so it will be handled by the GUI
        elif key == 'esc':
            return 'esc'
        else:
            self.frame.focus_position = 'footer'
        return super(ConsoleWidget, self).keypress(size, key)

    def write(self, text):
        """ Takes Markup and puts it on the console
        """
        self.history_listWalker.append(
            urwid.SelectableIcon(text))
        self.history_listWalker.set_focus(len(self.history_listWalker) - 1)

    def expand(self):
        """ Increase own size
        And set focus to the edit-field
        """
        self.height = 30

    def minimize(self):
        """ Decrease own size
        """
        self.height = 8


class MetaViewWidget(urwid.Frame):
    """ View for various Metadata of the current animation

    Displayed Data
        version (immutable)
        last edit (immutable)
        author  (mutable)
        description (mutable)
    """
    def __init__(self, ui, recorder):
        self.ui = ui
        self.rec = recorder
        self.name = urwid.Text([('caption2', 'Name: '), str(self.rec.name)])
        self.version = urwid.Text(
            [('caption2', 'Version: '), str(self.rec.version)])
        self.last_edit = urwid.Text(
            [('caption2', 'Last Edit: '), str(self.rec.last_edited)])
        self.author = urwid.Edit(
            ('caption2', "Author: "), str(self.rec.author))
        self.last_hostname = urwid.Text(
            [('caption2', "Edited on: "), str(self.rec.last_hostname)])
        self.description = urwid.Edit(
            ('caption2', 'Description: '), str(self.rec.description))
        self.pile = urwid.Pile([self.name, self.version,
                               self.last_edit, self.author, self.last_hostname, self.description])
        self.filler = urwid.Filler(self.pile)
        text = [('caption2', "Metadaten-Ansicht   "),
                ('red', "ESC: Abbrechen   "),
                ('green', "Enter: Speichern")]
        return super(MetaViewWidget, self).__init__(self.filler, urwid.Text(text))

    def keypress(self, size, key):
        if key == 'tab':
            try:
                self.pile.focus_position += 1
            except IndexError:
                self.pile.focus_position = 3
        elif key == 'enter':
            self.save()
            self.ui.display_frames()
            return
        elif key == 'esc':
            ilog.info('Meta-Edit abgebrochen')
            self.ui.display_frames()
            return
        return super(MetaViewWidget, self).keypress(size, key)

    def save(self):
        """ Write changes to the recorder
        """
        self.rec.description = self.description.get_edit_text()
        self.rec.author = self.author.get_edit_text()
        ilog.info('Meta-Edit gespeichert (nicht aber die Animation)')


class MotorViewWidget(urwid.Frame):
    def __init__(self):
        self.joints = Joints().actual()
        self.text = urwid.Text(motorIdsFormated)
        self.text.set_wrap_mode('clip')
        self.filler = urwid.Filler(self.text)
        caption = "Motorübersicht"
        return super(MotorViewWidget, self).__init__(self.filler, urwid.Text(caption, align='center'))

    def highlight(self, group):
        ilog.debug("Highligting Motor-Group %s" % group)
        highlight = self.joints.get_joints(group)
        if not highlight:
            ilog.warning("No motor found for group %s" % group)
            return False
        attrmap = {}
        for joint in highlight:
            mid = 'mid' + str(joint.cid)
            attrmap[mid] = 'mv_highlight'
        ilog.debug("Attrmap: %s" % attrmap)
        self.filler.body = urwid.AttrMap(urwid.Text(motorIdsFormated), attrmap)
        return True


class MotorInfoProvider():
    def __init__(self):
        self.joints = Joints().all()

    def display_motor_info(self, arg=""):
        matches = []
        # No specific info request, we give info on all motors
        if not arg:
            ilog.debug("No MotorInfo specification given, returning all Infos i have...")
            matches = self.joints

        # If we got a Motor ID given, just search for it
        elif arg.isdigit():
            try:
                arg = int(arg)
            except ValueError:
                # Can this even happen when arg.isdigit()?
                ilog.error(
                    "Thought %s was a int, but i appear to be in error...")
                return False
            try:
                match = self.joints.get_joint_by_cid(arg)
            except KeyError:
                # User might have given a random number get_joint_by_cid does
                # not check on its own
                ilog.warning(
                    "The given motor %i does not appear to exist!" % arg)
                return False

            # return Text Field list for use in the UI
            return [urwid.Text(self.formatted_motor_info(match))]

        # Otherwise search for a name match, or any tag matches
        else:
            for joint in self.joints:
                if joint.name.lower() == arg:
                    ilog.debug(
                        "Found exact match for MotorInfoRequest on %s" % arg)
                    self.text.set_text(self.formatted_motor_info(joint))
                    return True
                elif arg in joint.tags:
                    matches.append(joint)

        # No match, no Info
        if not matches:
            ilog.warning(
                "I could find no motors you could have meant by '%s'" % arg)
            return False

        new_texts = []
        for joint in matches:
            new_texts.append(urwid.Text(self.formatted_motor_info(joint)))
            #new_text.extend(self.formatted_motor_info(joint))
        return new_texts

    def formatted_motor_info(self, joint):
        """ Returns a urwid-formatted Info of the given "joint"
        """
        text = []
        text.append(('default', "Name: "))
        text.append(('mi_motor_name', str(joint.name) + "\n"))
        text.append(('default', "ID: "))
        text.append(('mi_motor_id', str(joint.cid) + "\n"))
        text.append(('default', "Tags:\n"))
        tags = ""
        for tag in joint.tags:
            tags += "    " + str(tag) + "\n"
        text.append(('mi_motor_tag', tags))
        if not joint.opposing:
            text.append(('default', "opposing motor: None\n\n"))
        else:
            text.append(('default', "opposing motor: %i\n" % joint.opposing))
            if joint.inverted:
                text.append(('default', "Motor IS inverted against his opposing motor\n\n"))
            else:
                text.append(('default', "Motor is NOT inverted against his opposing motor\n\n"))
        return text
