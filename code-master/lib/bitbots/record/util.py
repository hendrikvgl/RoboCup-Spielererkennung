#-*- coding:utf-8 -*-
"""
Utility Functions used by the record-gui
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Timon Giese <timon.giese@bit-bots.de>

History:
--------

    * 2014-06-30: UI Datenformate geändert im zuge der p-gain unterstützung
    * 2014-06-30: History angelegt, Modul ist aber bereits älter
"""

import logging
from urwid import Text
from bitbots.util import Joints
ilog = logging.getLogger('record-gui')  # internal logger

motors = Joints().names_ordered()


class property_proxy(property):
    """ Makes it possible to propagate propertys like::
            myprop = property_proxy('object', 'objectprop')
    """
    def __init__(self, proxy_attr, name):
        def _get(self):
            obj = getattr(self, proxy_attr)
            return getattr(obj, name)

        def _set(self, value):
            obj = getattr(self, proxy_attr)
            return setattr(obj, name, value)

        super(self.__class__, self).__init__(_get, _set)


class JsonConverter():
    """Provides conversion functions to convert between json-data and gui-values
    """

    def __init__(self):
        pass

    def get_joints(self, pose):
        """ Returns a list of all 24 possible joint values.
        When a joint is not specified by the json-pose, the value is
        set to "IGNORE".

        :param pose: *goals* dictionary from the json.
        :return: ordered list of joint-values
        """

        values = []
        for mot in motors:
            try:
                values.append(pose[mot])
            except KeyError:
                values.append("IGNORE")
        return values

    def get_keyframe_data(self, frame):
        """Provides a list of 26 entries as required by a gui-keyframe.

        :param frame: the keyframe dictionary from the .json
        :return: ordered list of 24 joint-values plus duration and pause values
        """
        values = {}
        if 'p' in frame:
            values['gains'] = self.get_joints(frame['p'])
        else:
            values['gains'] = self.get_joints({})
        try:
            values['goals'] = self.get_joints(frame['goals'])
            values['duration'] = frame['duration']
            values['pause'] = frame['pause']
        except KeyError as e:
            errmsg = "There was an terrible error while loading a keyframe. The Key %s could not be found!" % e
            ilog.warning(errmsg)
            return False
        return values

    def get_dict(self, keyframedata):
        """Converts keframedata from the gui back to a dictionary to be included in a .json

        :param keyframedata: the 26 Element-List from the GUI
        :return: a dictionary representing the keyframe
        """

        enum = enumerate(keyframedata['goals'])
        pose = {}
        for mot in motors:
            value = enum.next()[1]
            if not value == "IGNORE":
                pose[mot] = float(value)
        frame = {'goals': pose}

        enum = enumerate(keyframedata['gains'])
        gains = {}
        for mot in motors:
            value = enum.next()[1]
            if not value == "IGNORE":
                gains[mot] = float(value)
        frame['p'] = gains

        frame['duration'] = keyframedata['duration']
        frame['pause'] = keyframedata['pause']

        return frame


class MotorInfoProvider():
    def __init__(self):
        self.joints = Joints().all()

    def report_id(self, arg):
        """ Print out all ID belonging to the given Tag
        """
        matches = []
        for joint in self.joints:
            if joint.name.lower() == arg or arg in joint.tags:
                matches.append(joint.cid)
        if not matches:
            ilog.info("No Motor found in this Group!")
            return False

        ilog.info("%s" % sorted(matches))
        return True

    def get_motor_info(self, arg=""):
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
                ilog.error("Thought %s was a int, but i appear to be in error...")
                return False
            try:
                match = self.joints.get_joint_by_cid(arg)
            except KeyError:
                # User might have given a random number get_joint_by_cid does
                # not check on its own
                ilog.warning("The given motor %i does not appear to exist!" % arg)
                return False

            # return Text Field list for use in the UI
            return [Text(self.formatted_motor_info(match))]

        # Otherwise search for a name match, or any tag matches
        else:
            for joint in self.joints:
                if joint.name.lower() == arg:
                    ilog.debug("Found exact match for MotorInfoRequest on %s" % arg)
                    return([Text(self.formatted_motor_info(joint))])
                elif arg in joint.tags:
                    matches.append(joint)

        # No match, no Info
        if not matches:
            ilog.warning("I could find no motors you could have meant by '%s'" % arg)
            return False

        new_texts = []
        for joint in matches:
            new_texts.append(Text(self.formatted_motor_info(joint)))
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
                text.append(('default', "Motor IS inverted against the opposing motor\n\n"))
            else:
                text.append(('default', "Motor is NOT inverted against the opposing motor\n\n"))
        return text


def list_select(source_list, selector):
    indices = index_select(source_list, selector)
    outlist = []
    for index in indices:
        outlist.append(source_list[index])
    return outlist


def index_select(source_list, selector):
    """ Returns a list of input list-indexes based on a given selector

    .. todo:: Productionlist of allowed syntax

    """
    out_list = []

    if selector == 'all':
        return range(len(source_list))

    termlist = selector.split(',')
    current_position = 0
    length = len(source_list)
    for term in termlist:
        complex_term = term.split('-')
        # not a complex term at all:
        if len(complex_term) is 1:
            try:
                value = int(complex_term[0]) - 1  # selector indices start at 1
            except ValueError:
                ilog.warning("%s is not an integer!" % value)
                return []
            if value >= len(source_list):
                ilog.warning("Could not parse, because %i is too big" % (value + 1))
                return []
            if value < current_position:
                ilog.warning("Will not parse, because %i comes before the last parsed position %i and I suspect there is an error." % (value, current_position))
                return []
            out_list.append(value)
            current_position = value
            continue

        # complex term, better check to be sure
        if len(complex_term) is not 2:
            ilog.warning("Could not parse the part '%s'" % complex_term)
            return False
        try:
            low = int(complex_term[0]) - 1   # selector indices start at 1
            high = int(complex_term[1])      # no need to decrement because of [:] implementation
        except ValueError:
            ilog.warning("%s does not appear to consist of integers o.O" % complex_term)
            return []
        if high > length:
            ilog.warning("Could not parse, because %i is too big" % high)
            return []
        if low + 1 > high:
            ilog.warning("Could not parse, because %i is higher than %i" % (low, high))
            return []
        if low < current_position:
            ilog.warning("Will not parse, because %i comes before the last parsed position %i and I suspect there is an error." % (low, current_position))
            return []
        out_list += range(low, high)
        current_position = high - 1
    return out_list


def is_selector(string):
    """ Determines if a given String is a valid list-selector

    It cannot checkt if the selector will work on a given list,
    but it is good to check user-input in advance.
    """
    try:
        selector = str(string)
    except ValueError:
        ilog.warning("is_selector received a non string object. This is not acceptable!")
        return False
    terms = selector.split(',')
    last = 0
    for term in terms:
        pre, sep, post = term.partition('-')
        try:
            int(pre)
            if post is not '':
                int(post)
        except ValueError:
            ilog.debug("is_selector: Invalid because a selector-part contains non-int data: '%s' " % term)
            return False
        if post is not '' and pre > post:
            ilog.debug("is_selector: Invalid because the part '%s' is not in ascending order" % term)
            return False
        if pre < last:
            ilog.debug("is_selector: Invalid because the parts '%s' start-position is too low" % term)
            return False
        if post is not '':
            last = post
        else:
            last = pre
    return True
