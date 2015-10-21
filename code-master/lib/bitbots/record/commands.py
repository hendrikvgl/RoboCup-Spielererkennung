#-*-encoding:utf-8-*-
import logging
import yaml
import bitbots.util
from urwid import ExitMainLoop
from bitbots.util.resource_manager import find_all_animation_names, is_animation_name
from bitbots.record.util import is_selector, MotorInfoProvider

logger = logging.getLogger('record-gui')


class Commander():
    """ Object that controls execution, help and
    autocompletion for all record-script commands.
    """
    def __init__(self, c_handler=None, recorder=None, jm=None, ui=None):
        self.console_handler = c_handler
        self.record = recorder
        self.jm = jm  # JointManager from the module 'record'
        self.ui = ui
        self.helpmap = None  # Holds the help (if loading succeds)
        self.all_commands = {}  # Convinence dict holding merged commands and aliases
        self.aliases = {}  # Holds alias definitions (if loading succeds)
        self.motor_info_provider = MotorInfoProvider()
        self.commands = {
            'help': self.cmd_help,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
            'record': self.cmd_rec_record,
            'dump': self.cmd_rec_dump,
            'load': self.cmd_rec_load,
            'play': self.cmd_rec_play,
            'clear': self.cmd_rec_clear,
            'revert': self.cmd_rec_revert,
            'init': self.cmd_rec_init,
            'append': self.cmd_rec_append,
            'on': self.cmd_jm_on,
            'off': self.cmd_jm_off,
            'loglevel': self.cmd_loglevel,
            'copy': self.cmd_rec_copy,
            'move': self.cmd_rec_move,
            'pose': self.cmd_rec_pose,
            'desc': self.cmd_rec_desc,
            'meta': self.cmd_meta,
            'author': self.cmd_rec_author,
            'motors': self.cmd_motors,
            'motorinfo': self.cmd_motorinfo,
            'mirror': self.cmd_rec_mirror,
            'id': self.cmd_id,
            'undo': self.cmd_rec_undo,
            'redo': self.cmd_rec_redo,
            'xxxtestcommand': self.cmd_xxxtestcommand
        }

        self.autocompletions = {
            'load': self.ac_anim,
            'play': self.ac_anim,
            'append': self.ac_anim
        }

        self.load_aliases()
        self.load_help()

    def set_jm_ipc(self,ipc):
        self.jm.set_ipc(ipc)

    def cmd_loglevel(self, arguments):
        """ command function to set/get the loglevel
        """
        if len(arguments) > 1:
            logger.warn(
                "expected one or zero arguments, got %i" % (len(arguments)))
            return False
        if not arguments:
            logger.info(
                "Current loglevel is: %s" % self.console_handler.level)
            return True

        level = arguments[0]

        try:
            level = int(level)
        except ValueError:
            logger.warn("Loglevel must be an integer!")
            return False
        if 0 <= level <= 20:
            self.console_handler.setLevel(level)
            logger.info("Set Console Loglevel to %s" % level)
        elif 0 <= level <= 50:
            logger.warn("Console will not work properly at a loglevel this high! But I am doing as you please anyway...")
            self.console_handler.setLevel(level)
            logger.info("Set Console Loglevel to %s" % level)
        else:
            logger.warn(
                " %s is not a valid loglevel, ignoring command." % level)
            return False
        return True

    def cmd_quit(self, arguments):
        """ command function to quit the debugui
        """
        if arguments:
            logger.warn("What? Quit has no arguments.")
            return False
        logger.info("Quitting now...")
        raise ExitMainLoop

    def cmd_help(self, arguments):
        if not arguments:
            arguments = ['help']
        return self.ui.display_help(arguments)

    def cmd_rec_record(self, arguments):
        if not arguments:
            return self.record.record()
        if len(arguments) > 1:
            logger.warn(
                "record takes one argument at max! (got %s)" % len(arguments))
            return False
        else:
            try:
                arg = int(arguments[0])
                arg -= 1  # User-Presented list starts with position 1
                self.record.record(pos=arg)
            except ValueError:
                logger.warn("record argument must be a keyframe-number, not %s" % arguments[0])
                return False
        return True

    def cmd_rec_dump(self, arguments):
        if not arguments:
            logger.warn("No name specified. Use: dump <name>")
            return False
        if len(arguments) > 1:
            logger.warn("too many arguments for dump!")
            return False
        logger.info("speichern erfolgreich")
        return self.record.dump(arguments[0])

    def cmd_rec_load(self, arguments):
        if not arguments:
            logger.warn("Load what?")
            return False
        if len(arguments) > 1:
            logger.warn("Too many arguments for load. Use: load <name>")
            return False
        return self.record.load(arguments[0])

    def cmd_rec_play(self, arguments):
        if not arguments:
            return self.record.play()
        if len(arguments) is 1:
            arg = arguments[0]
            if is_animation_name(arg):
                return self.record.play(arg)
            elif is_selector(arg):
                return self.record.play(selector=arg)
            else:
                logger.warn("Your argument is neighter a animation-name nor a valid frame-selector")
                return False
        elif len(arguments) is 2:
            selector = arguments[0]
            name = arguments[1]
            if not is_animation_name(name):
                logger.warn("The Animation you asked for does not appear to exist")
                return False
            if not is_selector(selector):
                logger.warn("The selector you specified is invalid")
                return False
            return self.record.play(name, selector=selector)
        elif len(arguments) > 2:
            logger.warn("Too many arguments for play. Use: play [selector] [name]")
            return False

    def cmd_rec_clear(self, arguments):
        if arguments:
            logger.warn("What shall I do with the argument(s) ?!?")
            return False
        return self.record.clear()

    def cmd_rec_revert(self, arguments):
        if not arguments:
            return self.record.revert()
        elif len(arguments) is not 1:
            logger.warn(
                "Too many arguments for revert. Use: revert [framenumber]")
            return False
        return self.record.revert(arguments[0])

    def cmd_rec_init(self, arguments):
        if arguments:
            logger.warn("What shall I do with the argument(s) ?!?")
            return False
        return self.record.init()

    def cmd_rec_append(self, arguments):
        if not arguments:
            logger.warn("Please tell me _what_ to append!")
            return False
        if len(arguments) > 1:
            logger.info("Trying to append %s animations..." % len(arguments))
        failures = []
        for arg in arguments:
            if not self.record.append(arg):
                failures.append(arg)
        if failures:
            logger.error(
                "Could not append following animations: %s" % failures)
            return False
        logger.info("All animations appended successfully!")
        return True

    def cmd_rec_copy(self, arguments):
        if not arguments:
            logger.warn("Please tell me _what_ to copy!")
            return False
        elif len(arguments) > 2:
            logger.warn(
                "I cannot copy with so many arguments (%s)" % len(arguments))
            return False
        try:
            arg1 = int(arguments[0])
            if not arg1 > 0:
                raise ValueError
            if len(arguments) is 2:
                arg2 = int(arguments[1])
                if not arg2 > 0:
                    raise ValueError
            else:
                arg2 = None
        except ValueError:
            logger.warn("All arguments to copy must be Keyframe-Id's!")
            return False
        return self.record.copy(arg1, arg2)

    def cmd_rec_move(self, arguments):
        if not arguments:
            logger.warn("Please tell me _what_ to move!")
            return False
        elif len(arguments) is not 2:
            logger.warn("move needs exactly 2 arguments")
            return False
        try:
            arg1 = int(arguments[0])
            arg2 = int(arguments[1])
            if not arg1 > 0 or not arg2 > 0:
                raise ValueError
        except ValueError:
            logger.warn("All arguments to move must be Keyframe-Id's!")
            return False
        return self.record.move(arg1, arg2)

    def cmd_rec_pose(self, arguments):
        if not arguments:
            logger.warn("Please tell me _what_ pose I should take!")
            return False
        elif len(arguments) is not 1:
            logger.warn("pose takes exactly _one_ keyframe-id as argument!")
            return False
        try:
            arg = int(arguments[0])
        except ValueError:
            logger.warn("invalid keyframe-id!")
            return False
        if not arg > 0:
            logger.warn("invalid keyframe-id")
            return False
        return self.record.pose(arg)

    def cmd_rec_mirror(self, arguments):
        if not arguments or not len(arguments) == 2:
            logger.warn("Usage: mirror <selector> <tag>")
            return False
        selector = arguments[0]
        tag = arguments[1]
        return self.record.mirror(selector, tag)

    def cmd_jm_on(self, arguments):
        if not arguments:
            return self.jm.on()
        if len(arguments) > 1:
            logger.info("Trying to switch on %s groups" % len(arguments))
            failures = []
            for arg in arguments:
                if not self.jm.on(arg):
                    failures.append(arg)
            if failures:
                logger.warn("Following Groups failed: %s" % failures)
                return False
            else:
                return True
        return self.jm.on(arguments[0])

    def cmd_jm_off(self, arguments):
        if not arguments:
            return self.jm.off()
        if len(arguments) > 1:
            logger.info("Trying to switch off %s groups" % len(arguments))
            failures = []
            for arg in arguments:
                if not self.jm.off(arg):
                    failures.append(arg)
            if failures:
                logger.warn("Following Groups failed: %s" % failures)
                return False
            else:
                return True
        return self.jm.off(arguments[0])

    def cmd_rec_desc(self, arguments):
        """ modifies description.
        Currently it displays for no arguments, otherwise it takes all
        arguments as the description-text
        using the command "meta" there will be a special edit/display window
        for the Animation Metadata
        """
        if not arguments:
            logger.info(self.record.description)
            return True
        else:
            desc = ""
            for item in arguments:
                desc += ' ' + item
            self.record.description = desc
            logger.info("Description changed (Animation not saved)")
            return True

    def cmd_rec_author(self, arguments):
        if not arguments:
            logger.info(self.record.author)
            return True
        else:
            author = ""
            for item in arguments:
                author += ' ' + item
            self.record.author = author
            logger.info("Author changed (Animation not saved)")
            return True

    def cmd_rec_undo(self, arguments):
        if not arguments:
            return self.record.undo()
        elif len(arguments) > 1:
            logger.info("Usage: undo [amount]")
            return False
        else:
            try:
                amount = int(arguments[0])
            except ValueError:
                logger.info("The amount must be a integer")
                return False
        return self.record.undo(amount)

    def cmd_rec_redo(self, arguments):
        if not arguments:
            return self.record.redo()
        elif len(arguments) > 1:
            logger.info("Usage: redo [amount]")
            return False
        else:
            try:
                amount = int(arguments[0])
            except ValueError:
                logger.info("The amount must be a integer")
                return False
        return self.record.redo(amount)

    def cmd_meta(self, arguments):
        if not arguments:
            self.ui.display_meta()
            return True
        else:
            logger.warn("What shall I do with the argument(s) ?!?")
            return False

    def cmd_motors(self, arguments):
        """ Shows a ASCII-Art overview of the darwin-motors.
        if there is a argument it will be interpreted as
        motor group and the motors belonging to that group
        will be highlighted
        """
        if not arguments:
            return self.ui.display_motor_ids()
        elif len(arguments) is 1:
            return self.ui.display_motor_ids(arguments[0].lower())
        else:
            logger.warn("Too many arguments (must be one or none)!")
            return False

    def cmd_motorinfo(self, arguments):
        """ Gives Information on motors or a subset of motors,
        when an argument is given
        """
        if not arguments:
            return self.ui.display_motor_info()
        elif len(arguments) is 1:
            return self.ui.display_motor_info(arguments[0].lower())
        else:
            logger.warn("Too many arguments (must be one or none)!")
            return False

    def cmd_id(self, arguments):
        """ Returns the Motor ID(s) belonging to a given tag
        """
        if not arguments:
            logger.info("Usage: id <motortag>")
            return False
        if len(arguments) > 1:
            logger.warning("Sorry currently you can ask for only ONE tag")
            return False
        return self.motor_info_provider.report_id(arguments[0].lower())

    def cmd_xxxtestcommand(self, arguments):
        """ Testcommand to test for the Commander Connectivity.
        Changing this will cause a test to fail :)
        """
        logger.info("pong (Der Commander hört dir zu)")
        return 42

    def get_commands(self):
        return self.commands

    def autocomplete(self, cmd, arguments):

        # no arguments => extend command itself
        if not arguments:
            if not cmd:
                logger.debug("Nothing to autocomplete")
                return False
            possible = []  # possible completions
            for key in self.all_commands:
                if key.startswith(cmd):
                    possible.append(key)

        # We have some arguments => extend them if possible
        else:
            if cmd in self.autocompletions:
                possible = self.autocompletions[cmd](arguments)
            else:
                logger.warn("Sorry, autocomplete not implemented here (yet)")
                return False

        # Sort and return our findings
        # The UI will have to do the rest
        possible = sorted(set(possible))
        return possible

    def has_command(self, cmd):
        return cmd in self.commands or cmd in self.aliases

    def run(self, command, arguments):
        """ Execute given command with given parameters

        :param str command: Command to be executed
        :param list arguments: List of arguments
        """
        if not command in self.commands:
            if command in self.aliases:
                command = self.aliases[command]
            else:
                logger.warn('whoopsie! Command %s does not appear to exist!')
                return False
        new_args = []
        for argument in arguments:
            if type(argument) == str:
                new_args.append(argument.lower())
            else:
                new_args.append(argument)
        success = self.commands[command](new_args)
        if not success:
            logger.debug("record-command returned as a failure")
        return success

    def load_help(self):
        """ Parse the yaml-file with the help information
        """
        try:
            path = bitbots.util.find_resource('record_help.yaml')
            with open(path, 'r') as f:
                self.helpmap = yaml.load(f)
                logger.debug('help-file loaded')
        except IOError:
            # missing help is a serious fault, but does not force program termination
            logger.warn('help-file could not be opened! - no help availiable')
            self.helpmap = None
        except yaml.YAMLError as e:
            logger.warn('help-file could not be parsed! - no help availiable')
            logger.warn("Error in help-file: %s" % e)

    def load_aliases(self):
        """ Parse the yaml-file with the command alias information
        """
        try:
            path = bitbots.util.find_resource('record_aliases.yaml')
            with open(path, 'r') as f:
                self.aliases = yaml.load(f)
                logger.debug('alias-file loaded')
        except IOError:
            # Missing Aliases are not considered to be critical, though we
            # should log it.
            logger.debug('Alias-file could not be opened! - no aliases availiable')
            return False

        # Next verify aliases. If the aliased command is unkown, we shall
        # remove it from the dict
        for alias, command in self.aliases.copy().iteritems():
            if alias in self.commands:
                logger.warn("The alias '%s' would override the existing command. I am sorry Dave, I'm afraid I can't do that!'" % alias)
                del self.aliases[alias]
                continue
            if not command in self.commands:
                logger.warn("The command '%s' for the alias '%s' could not be found!" % (command, alias))
                del self.aliases[alias]

        # For convinece we build a merged dict of aliases and 'real' commands
        self.all_commands = self.aliases.copy()
        self.all_commands.update(self.commands)
        return True

    def ac_anim(self, arguments):
        if not arguments:
            logger.warn("animation autocomplete received no string to complete")
            return []
        animstart = arguments[-1]
        animations = find_all_animation_names()
        if not animations:
            logger.debug("It seems the Resource Manager found no animation at all o.O")
        possible = []

        for anim in animations:
            if anim.startswith(animstart):
                possible.append(anim)
        return possible
