#!/usr/bin/env python
#-*-encoding:utf-8-*-
"""

.. moduleauthor:: Timon Giese<timon.giese@bit-bots.de>

History:
    2013-12-08: Test für Animationsdateien hinzugefügt
    2014-02-04: Mehr Command-Tests (meta, author, descr)

"""
import unittest
import logging
import json
import bitbots.ipc as ipc
import bitbots.record.util as bbutil
import time
import os
import signal
import multiprocessing

from ui import Mainframe
#from mock import Mock
from bitbots.record.commands import Commander
from bitbots.record.record import Recorder, JointManager
from bitbots.util.resource_manager import find_all_animations
from urwid import ExitMainLoop
from shutil import move
from copy import deepcopy
from bitbots.motion.simulationmotionserver import simulate

_global_ipc = None
_simulation_process = None
#_stdout_handler = None


def setUpModule():
    """ SetUp a simulation framework for safe(er) Testing.

    Some record-functions can only be tested when a motion exists,
    it could be pretty desatstrous to use a real motion (because the
    robot would move unexpectedly), but setting up a simulation
    might would also disturb running robot operations (and you dont want
    to break things by testing).

    Our solution is to move an existing ipc-file
    (which is used by new processes only),
    start our IPC (which then uses a completely different Memory section)
    and move the ipc-file back immediately to reduce risk of a new started
    Process using the "dummy" ipc.

    This should ensure that any real robot processes can still communicate,
    while all Tested-processes can work on a dummy-ipc.
    """
    global _global_ipc
    global _simulation_process
    #global _stdout_handler

    #_stdout_handler = logging.StreamHandler()

    print "Trying to set up Simulation-Environment..."

    # First we move the orignial IPC-Data out of the way
    moved = True
    try:
        print "Temporarily moving original IPC-File"
        move('/dev/shm/DarwinIPC', '/tmp/DarwinIPC_backup')
    except IOError:
        print "No IPC-File found. That's OK I guess..."
        moved = False
    # Now we init the IPC
    # I dont really expect an Exception,
    # but we need to be *damn* sure the File is moved back
    # even if the ipc-init fails.
    try:
        _global_ipc = ipc.SharedMemoryIPC()
    except BaseException as e:
        raise e
    # move the original IPC-file back no matter what happens.
    # granted we *have* an original. Else never mind...
    finally:
        if moved:
            try:
                move('/tmp/DarwinIPC_backup', '/dev/shm/DarwinIPC')
                print "Original IPC-File restored!"
            except IOError:
                print "CRITICAL: Failed to restore original IPC-File!!!"

    print "Starting simulation process..."
    _simulation_process = multiprocessing.Process(target=simulate, args=(_global_ipc,))
    _simulation_process.start()

    print "... waiting for startup to finish ..."
    deadline = time.time() + 10
    while not _global_ipc.controlable:
        if time.time() > deadline:
            print "\n###################################################"
            print "# WARNING: Simulation did not initialise in time! #"
            print "###################################################"
            print "(Thus tests may fail that might otherwise succed)"
            return
        else:
            time.sleep(0.1)
    print "... simulation initialised!"
    print "Running Tests now:\n"


def tearDownModule():
    """ Ends the Simulation-Server
    """
    if not _simulation_process.is_alive():
        print "\n\n WARNING: simulation died before the Tests ended!"
        print "(Thus some tests dependent on the simulation might have failed.)"
        return
    print "\n\nTearing down Simulation"
    os.kill(_simulation_process.pid, signal.SIGTERM)
    deadline = time.time() + 5
    while _simulation_process.is_alive():
        if time.time() > deadline:
            print "Simulation did not end in time! Attempting SIGKILL"
            os.kill(_simulation_process.pid, signal.SIGKILL)
            deadline = time.time() + 5
            while _simulation_process.is_alive():
                if time.time() > deadline:
                    print "Simulation still survived our murderous attempt o.O"
                    print "Check for a running simulation yourself!"
                    return
                time.sleep(0.1)
            break
        time.sleep(0.1)
    print "Simulation is dead. It wont be missed."


class TestCommands(unittest.TestCase):
    longMessage = True

    def setUp(self):
        """ Run prior to each test_* Method
        """
        # logging handler (collects user-feedback, debug and errors)
        # You might want to specify a logger and real handler here
        # to pass to the recorder and joint manager in order
        # to obtain useful debugging messages for failure-tests.
        self.ipc = _global_ipc
        self.logger = logging.getLogger('record-gui')
        self.handler = logging.NullHandler()
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
        self.ui = Mainframe(ui_debug=True, ipc=self.ipc)
        self.recorder = Recorder(self.ipc, self.ui)
        self.recorder.dump_path = "/tmp/%s.json"
        self.jm = JointManager(self.ipc)
        self.commander = Commander(
            self.handler, self.recorder, self.jm, self.ui)

    def tearDown(self):
        """ Run after each test_* Method
        """
        self.handler.flush()

    def test_loglevel(self):
        reason = 'expected True as a return for loglevel 10'
        test = self.commander.run('loglevel', [10])
        self.assertTrue(test, reason)

        reason = 'incorrect handler-level after set'
        test = self.handler.level == 10
        self.assertTrue(test, reason)

        reason = 'expected True as a return for loglevel 0'
        test = self.commander.run('loglevel', [0])
        self.assertTrue(test, reason)

        reason = 'incorrect handler-level after set'
        test = self.handler.level == 0
        self.assertTrue(test, reason)

        reason = 'expected True as a return for loglevel 50'
        test = self.commander.run('loglevel', [50])
        self.assertTrue(test, reason)

        reason = 'incorrect handler-level after loglevel 50'
        test = self.handler.level == 50
        self.assertTrue(test, reason)

        reason = 'expected Failure for loglevel 1337'
        test = self.commander.run('loglevel', [1337])
        self.assertFalse(test, reason)

        reason = 'expected Failure for loglevel -1'
        test = self.commander.run('loglevel', [-1])
        self.assertFalse(test, reason)

        reason = 'expected Failure for non-integer loglevel'
        test = self.commander.run('loglevel', ['foo'])
        self.assertFalse(test, reason)

        reason = 'expected Failure for non-integer loglevel'
        test = self.commander.run('loglevel', ['0.5'])
        self.assertFalse(test, reason)

        reason = 'expected Success for loglevel command without arguments'
        test = self.commander.run('loglevel', [])
        self.assertTrue(test, reason)

        reason = 'expected clean Failure for loglevel command without arguments'
        test = self.commander.run('loglevel', ['1', '2', '3'])
        self.assertFalse(test, reason)

    def test_quit(self):
        # Test if quit results in an exit signal for urwid:
        with self.assertRaises(ExitMainLoop):
            self.commander.run('quit', [])

        reason = 'quit should not take arguments'
        test = self.commander.run('quit', ['bugging', 'me'])
        self.assertFalse(test, reason)

    def test_help(self):
        """ Functionality test, to ensure help does not crash when called
        """

        reason = 'help should return True'
        test = self.commander.run('help', [])
        self.assertTrue(test, reason)

        reason = 'help on topic "help" should return True'
        test = self.commander.run('help', ['help'])
        self.assertTrue(test, reason)

        reason = 'help on nonexistent topic should Fail'
        test = self.commander.run('help', ['xxxnonexistent'])
        self.assertFalse(test, reason)

    def test_help_coverage(self):
        """ Attempt getting help for any command known
        """
        reason = 'Missing help for command(s): '
        test = True
        for command in self.commander.commands:
            if not self.commander.run('help', [command]):
                reason += "%s " % command
                test = False
        self.assertTrue(test, reason)

    def test_record(self):
        reason = 'record with too many arguments should return False'
        test = self.commander.run('record', [1, 2, 3])
        self.assertFalse(test, reason)

        reason = 'record with invalid argument should return False'
        test = self.commander.run('record', ['nothing'])
        self.assertFalse(test, reason)

        reason = 'recorder should not have a keyframe after record'
        test = self.recorder.anim
        self.assertFalse(test, reason)

        reason = 'record should return True when successful'
        test = self.commander.run('record', [])
        self.assertTrue(test, reason)

        reason = 'recorder should have a keyframe after record'
        test = self.recorder.anim
        self.assertTrue(test, reason)

        reason = 'undoing record should return True when successful'
        test = self.commander.run('undo', [])
        self.assertTrue(test, reason)

        reason = 'recorder should have no keyframe after undoing record'
        test = self.recorder.anim
        self.assertFalse(test, reason)

        reason = 'redoing record should return True when successful'
        test = self.commander.run('redo', [])
        self.assertTrue(test, reason)

        reason = 'recorder should have a keyframe after redoing record'
        test = self.recorder.anim
        self.assertTrue(test, reason)

        reason = 'recording to a valid position should not fail'
        test = self.commander.run('record', [1])
        self.assertTrue(test, reason)

    def test_clear(self):
        reason = 'load must succed for this test to run'
        test = self.commander.run('load', ['xxxtestanim'])
        self.assertTrue(test, reason)

        reason = 'clear should return True when succesfull'
        test = self.commander.run('clear', [])
        self.assertTrue(test, reason)

        reason = 'recorder.anim should be empty after clear'
        test = self.recorder.anim
        self.assertFalse(test, reason)

        reason = 'undoing clear should succed'
        test = self.commander.run('undo', [])
        self.assertTrue(test, reason)

        reason = 'recorder.anim should be restored after undoing clear'
        test = self.recorder.anim
        self.assertTrue(test, reason)

        reason = 'redoing clear should succed'
        test = self.commander.run('redo', [])
        self.assertTrue(test, reason)

        reason = 'recorder.anim should be empty after redoing clear'
        test = self.recorder.anim
        self.assertFalse(test, reason)

        reason = 'clear should fail when arguments are given'
        test = self.commander.run('clear', ['nothing'])
        self.assertFalse(test, reason)

    def test_revert(self):
        reason = 'revert should fail when there is nothing to revert'
        test = self.commander.run('revert', [])
        self.assertFalse(test, reason)

        self.recorder.anim = [1, 2, 3, 4, 5]

        # We do stuff in the Recorder the UI is not aware of
        # so we exchange the two methods in the ui for a dummy
        def nop(*args, **kwargs):
            pass
        self.ui.pop_keyframe = nop
        self.ui.display_keyframes = nop

        self.commander.run('revert', [])
        reason = 'wrong item number in animations after revert'
        test = self.recorder.anim == [1, 2, 3, 4]
        self.assertTrue(test, reason)

        self.commander.run('revert', [2])
        reason = '2 should not be in the recorder after we reverted it!'
        test = self.recorder.anim == [1, 3, 4]
        self.assertTrue(test, reason)

        self.commander.run('undo', [])
        reason = 'undoing the revert should work'
        test = self.recorder.anim == [1, 2, 3, 4]
        self.assertTrue(test, reason)

        self.commander.run('redo', [])
        reason = 'redoing the undone revert should work'
        test = self.recorder.anim == [1, 3, 4]
        self.assertTrue(test, reason)

    def test_motors(self):
        reason = "motors command ohne parameter sollte klappen"
        test = self.commander.run('motors', [])
        self.assertTrue(test, reason)

        reason = "motors command mit UpperCased motorgruppe sollte funzen"
        test = self.commander.run('motors', ['LArm'])
        self.assertTrue(test, reason)

        reason = "motors command mit lowerCased motorgruppe sollte funzen"
        test = self.commander.run('motors', ['larm'])
        self.assertTrue(test, reason)

    def test_init_run(self):

        reason = 'successful init should return True'
        test = self.commander.run('init', [])
        self.assertTrue(test, reason)

        reason = 'init should not accept arguments'
        test = self.commander.run('init', ['never'])
        self.assertFalse(test, reason)

    def test_play(self):

        reason = "play could not be tested because 'record' failed"
        test = self.commander.run('record', [])
        self.assertTrue(test, reason)

        reason = "play without parameters failed"
        test = self.commander.run('play', [])
        self.assertTrue(test, reason)

        reason = "play with animation-name failed"
        test = self.commander.run('play', ['xxxtestanim'])
        self.assertTrue(test, reason)

    def test_append(self):

        reason = 'append should not allow to append nothing'
        test = self.commander.run('append', [])
        self.assertFalse(test, reason)

        reason = 'append xxxtestanim should work, unless the animation is missing'
        test = self.commander.run('append', ['xxxtestanim'])
        self.assertTrue(test, reason)

        reason = 'recorder.anim should not be empty after append'
        test = self.recorder.anim
        self.assertTrue(test, reason)

        reason = 'undo after append should succed'
        test = self.commander.run('undo', [])
        self.assertTrue(test, reason)

        reason = 'undo after append should leave a empty animation'
        test = self.recorder.anim
        self.assertFalse(test, reason)

        reason = 'redo after undone append should succed'
        test = self.commander.run('redo', [])
        self.assertTrue(test, reason)

        reason = 'redoing after undone append should work'
        test = self.recorder.anim
        self.assertTrue(test, reason)

        self.recorder.anim = []  # empty the animation for the next step
        reason = 'append should accept multiple items to append'
        test = self.commander.run('append', ['xxxtestanim', 'xxxtestanim'])
        self.assertTrue(test, reason)

        reason = 'we should have received multiple items'
        test = len(self.recorder.anim) is 4
        self.assertTrue(test, reason)

    def test_move(self):
        self.assertFalse(self.commander.run('move', [1, 2]),
                         'move should not succed when keyframes dont exist')
        dummy1 = {'goals': {'foo': 1}, 'duration': 1, 'pause': 1}
        dummy2 = {'goals': {'foo': 2}, 'duration': 2, 'pause': 2}
        dummy3 = {'goals': {'foo': 3}, 'duration': 3, 'pause': 3}
        dummy4 = {'goals': {'foo': 4}, 'duration': 4, 'pause': 4}
        dummy5 = {'goals': {'foo': 5}, 'duration': 5, 'pause': 5}

        animdummys = [dummy1, dummy2, dummy3, dummy4, dummy5]
        self.recorder.anim = deepcopy(animdummys)

        reason = 'move should not accept empty arguments'
        test = self.commander.run('move', [])
        self.assertFalse(test, reason)

        reason = 'move should not accept only one argument'
        test = self.commander.run('move', [1])
        self.assertFalse(test, reason)

        reason = 'move should succed for valid keyframes'
        test = self.commander.run('move', [1, 2])
        self.assertTrue(test, reason)

        reason = 'move 1 2 should be invariant'
        test = self.recorder.anim == animdummys
        self.assertTrue(test, reason)

        original = deepcopy(self.recorder.anim)
        reason = 'move should succed for valid keyframes'
        test = self.commander.run('move', [2, 4])
        self.assertTrue(test, reason)

        reason = 'expected a different list after move 2, 4'
        test = self.recorder.anim == [dummy1, dummy3, dummy2, dummy4, dummy5]
        self.assertTrue(test, reason)

        undone = deepcopy(self.recorder.anim)
        reason = 'undo should work after a succesfull move'
        test = self.commander.run('undo', [])
        self.assertTrue(test, reason)

        reason = 'undo should have worked after a succesfull move'
        test = self.recorder.anim == original
        self.assertTrue(test, reason)

        reason = 'redoing an undone move should succed'
        test = self.commander.run('redo', [])
        self.assertTrue(test, reason)

        reason = 'redoing an undone move should have worked'
        test = self.recorder.anim == undone
        self.assertTrue(test, reason)

        reason = 'move should not succed for bullshit input'
        test = self.commander.run('move', ["beer", "fridge"])
        self.assertFalse(test, reason)

    def test_mirror(self):
        reason = "Mirror on nonexistent keyframe must fail"
        test = self.commander.run('mirror', ['1', 'left'])
        self.assertFalse(test, reason)

        reason = 'working record command is a precondition for this test'
        test = self.commander.run('record', [])
        self.assertTrue(test, reason)

        reason = "Mirror left on existent keyframe should succed"
        test = self.commander.run('mirror', ['1', 'left'])
        self.assertTrue(test, reason)

        reason = "Mirror hips on existent keyframe should fail"
        test = self.commander.run('mirror', ['1', 'hips'])
        self.assertFalse(test, reason)

        self.commander.run('record', [])
        self.commander.run('record', [])
        oldstate = deepcopy(self.recorder.anim)
        reason = "Mirror left on multiple keyframes should succed"
        test = self.commander.run('mirror', ['all', 'left'])
        self.assertTrue(test, reason)

        reason = "Mirror should have worked"
        test = True
        for keyframe in self.recorder.anim:
            if (
                not keyframe['goals']['LKnee'] == - keyframe['goals']['RKnee']
                or not keyframe['goals']['LToe'] == - keyframe['goals']['RToe']
                or not keyframe['goals']['LHipRoll'] == keyframe['goals']['RHipRoll']  # these motors are not inverted
            ):
                test = False
        self.assertTrue(test, reason)

        undostate = deepcopy(self.recorder.anim)
        reason = "undo after mirror schould succed"
        test = self.commander.run('undo', [])
        self.assertTrue(test, reason)

        reason = "undo after mirror schould work"
        test = self.recorder.anim == oldstate
        self.assertTrue(test, reason)

        reason = "redo after undone mirror should succed"
        test = self.commander.run('redo', [])
        self.assertTrue(test, reason)

        reason = "redo after undone mirror should work"
        test = self.recorder.anim == undostate
        self.assertTrue(test, reason)

    def test_copy(self):
        self.assertFalse(self.commander.run('copy', [1, 2]),
                         'copy should not succed when keyframes dont exist')

        dummy1 = {'goals': {'foo': 1}, 'duration': 1, 'pause': 1}
        dummy2 = {'goals': {'foo': 2}, 'duration': 2, 'pause': 2}
        dummy3 = {'goals': {'foo': 3}, 'duration': 3, 'pause': 3}

        animdummys = [dummy1, dummy2, dummy3]
        self.recorder.anim = animdummys
        self.assertFalse(self.commander.run('copy', []),
                         'copy should not accept empty arguments')
        self.assertTrue(self.commander.run('copy', [1]),
                        'copy should accept one valid argument')
        self.assertEqual(self.recorder.anim, [dummy1, dummy1, dummy2, dummy3],
                         'copy should not result in %s' % self.recorder.anim)
        self.recorder.anim = [dummy1, dummy2, dummy3]
        self.assertTrue(self.commander.run('copy', [3, 1]),
                        'copy should succed for two valid arguments')
        self.assertEqual(self.recorder.anim, [dummy3, dummy1, dummy2, dummy3],
                         'copy should not result in %s' % self.recorder.anim)
        self.recorder.anim = [dummy1, dummy2, dummy3]
        self.assertTrue(self.commander.run('copy', [1, 3]),
                        'copy should succed for two valid arguments')
        self.assertEqual(self.recorder.anim, [dummy1, dummy2, dummy1, dummy3],
                         'copy should not result in %s' % self.recorder.anim)
        self.recorder.anim = [dummy1, dummy2, dummy3]
        self.assertTrue(self.commander.run('copy', [1, 4]),
                        'copy should succed for two valid arguments')
        self.assertEqual(self.recorder.anim, [dummy1, dummy2, dummy3, dummy1],
                         'copy should not result in %s' % self.recorder.anim)
        self.assertFalse(self.commander.run('copy', ["beer", "freezer"]),
                         'move should not succed for bullshit')
        self.assertFalse(self.commander.run('copy', [1, "freezer"]),
                         'move should not succed for bullshit')

    def test_pose(self):
        self.assertFalse(self.commander.run('pose', [1]),
                         'pose for non-existent Keyframe should fail')
        self.commander.run('record', [])
        self.assertTrue(self.commander.run('pose', [1]),
                        'pose for existent Keyframe should succeed')
        self.assertFalse(self.commander.run('pose', []),
                         'pose without arguments should fail')
        self.assertFalse(self.commander.run('pose', ['foo']),
                         'pose with bullshit argument should fail')

    def test_on(self):
        self.assertTrue(self.commander.run('on', []),
                        'singleton on should return true')
        self.assertTrue(self.commander.run('on', ['Larm']),
                        'on with capital tag should work')
        self.assertTrue(self.commander.run('on', ['larm']),
                        'on with lowercase tag should work')

    def test_off(self):
        self.assertTrue(self.commander.run('off', []),
                        'singelton off should return true')
        self.assertTrue(self.commander.run('off', ['Larm']),
                        'off with capital tag should work')
        self.assertTrue(self.commander.run('off', ['larm']),
                        'off with lowercase tag should work')

    def test_dump_and_load(self):
        """ Tests dumping and loading of animations.
        """
        # First record something so the rest might work
        self.commander.run('record', [])

        reason = 'dumping without argument should not succed'
        test = self.commander.run('dump', [])
        self.assertFalse(test, reason)

        reason = 'dumping with more than one argument should not succed'
        test = self.commander.run('dump', ['1', '2', '3'])
        self.assertFalse(test, reason)

        reason = 'loading without argument should not succed'
        test = self.commander.run('load', [])
        self.assertFalse(test, reason)

        reason = "Loading xxxtesanim should succed"
        test = self.commander.run('load', ['xxxtestanim'])
        self.assertTrue(test, reason)

        reason = 'dumping on test_dump should succed after load'
        test = self.commander.run('dump', ['test_dump'])
        self.assertTrue(test, reason)

        reason = 'loading the previously dumped test_dump should work'
        anim = self.recorder.anim  # save the current animation
        self.recorder.anim = None  # remove the current animation
        test = self.commander.run('load', ['test_dump'])
        self.assertTrue(test, reason)
        reason = 'the loaded animation should match the dumped one'
        self.assertEquals(anim, self.recorder.anim, reason)

        reason = 'loading with more than one argument should not succed'
        test = self.commander.run('load', ['test_dump', 'test_dump', 'test_dump'])
        self.assertFalse(test, reason)

    def test_meta(self):
        reason = "meta-command without parameters should succeed"
        self.assertTrue(self.commander.run('meta', []), reason)

    def test_author(self):
        reason = "author-command without parameters should succeed"
        self.assertTrue(self.commander.run('author', []), reason)

        reason = "author-command with one parameter should succeed"
        self.assertTrue(self.commander.run('author', ['Niemand']), reason)

    def test_alias(self):
        reason = "the testalias should work, maybe it was deleted from the alias-definition?"
        self.assertTrue(self.commander.run('xxxtestalias', []), reason)

    def test_description(self):
        reason = "descr-command without parameters should succeed"
        self.assertTrue(self.commander.run('author', []), reason)

        reason = "descr-command with more than one parameter should succeed"
        self.assertTrue(
            self.commander.run('author', ['Niemand', 'hat', 'die']), reason)

    def test_motorinfo(self):
        # positive tests
        reason = "motorinfo command without parameters should succeed"
        self.assertTrue(self.commander.run('motorinfo', []), reason)

        reason = "motorinfo command with valid motor name (Camle-Case) should succeed"
        self.assertTrue(
            self.commander.run('motorinfo', ['RShoulderPitch']), reason)

        reason = "motorinfo command with valid motor name (lowercased) should succeed"
        self.assertTrue(
            self.commander.run('motorinfo', ['rshoulderpitch']), reason)

        reason = "motorinfo command with valid motor id should succeed"
        self.assertTrue(self.commander.run('motorinfo', ['10']), reason)

        reason = "motorinfo command with valid motor tag (CamelCase) should succeed"
        self.assertTrue(self.commander.run('motorinfo', ['LArm']), reason)

        reason = "motorinfo command with valid motor tag (lowercased) should succeed"
        self.assertTrue(self.commander.run('motorinfo', ['larm']), reason)

        # negative tests
        reason = "motorinfo command with bullshit motor input should fail (but not crash)"
        self.assertFalse(
            self.commander.run('motorinfo', ['Heidelbeersalat']), reason)

        reason = "motorinfo command with bullshit motor input should fail (but not crash)"
        self.assertFalse(self.commander.run('motorinfo', ['1337']), reason)


class TestAnimations(unittest.TestCase):
    """ Animationsdateien im Anim-dir auf fehler testen
    """
    def __init__(self, methodName='runTest'):
        self.files = find_all_animations()
        super(TestAnimations, self).__init__(methodName)

    def test_animation_syntax(self):
        """ Test auf Syntaxfehler in den Animationsdateien
        """
        errorfiles = []
        for animation in self.files:
            with open(animation) as fp:
                try:
                    json.load(fp)
                except ValueError:
                    errorfiles.append(animation)
        self.assertFalse(errorfiles, "Folgende Animationen enthalten syntaxfehler: %s" % errorfiles)


class TestConsole(unittest.TestCase):
    def setUp(self):
        self.ipc = _global_ipc
        # logging handler (collects user-feedback, debug and errors)
        # You might want to specify a logger and real handler here
        # to pass to the recorder and joint manager in order
        # to obtain useful debugging messages for failure-tests.
        self.handler = logging.NullHandler()
        #self.ui = Mock(spec=Mainframe)
        self.ui = Mainframe(ui_debug=True)
        self.recorder = Recorder(self.ipc, self.ui)
        self.recorder.dump_path = "/tmp/%s.json"
        self.jm = JointManager(self.ipc)
        self.commander = Commander(self.handler, self.recorder, self.jm)
        self.console = self.ui.console

    def tearDown(self):
        pass

    def testCommanderConnection(self):
        self.console.edit.edit_text = 'xxxtestcommand'
        self.console.process_input()
        result = self.console.history_listWalker[-1].text
        resultwish = "pong (Der Commander hört dir zu)"
        failmsg = "Commander über die Console angeschrieben, aber nicht die gewünschte Antwort erhalten (war: %s)" % result
        self.assertEqual(result, resultwish, failmsg)

    def testCommandHistoryBasic(self):
        # Existierendes Testkommando
        self.console.edit.edit_text = 'xxxtestcommand'
        self.console.process_input()
        self.console.com_history_up()
        failmsg = "letztes Record-Kommando konnte nicht wiederhergestellt werden"
        self.assertEquals(
            self.console.edit.edit_text, 'xxxtestcommand', failmsg)

    def testCommandHistoryExtended(self):
        # Mülleingabe (sollte auch geloggt werden)
        self.console.edit.edit_text = 'foo'
        self.console.process_input()
        failmsg = "01 Eingabezeile wurde nach dem letzten Kommando nicht geleert"
        self.assertEquals(
            self.console.edit.edit_text, '', failmsg)
        self.console.com_history_up()
        failmsg = "01 History-Resultat entsprach nicht den erwartungen"
        self.assertEquals(
            self.console.edit.edit_text, 'foo', failmsg)
        self.console.com_history_up()
        self.console.com_history_up()
        failmsg = "02 History-Resultat (nach versuchtem überschreiten der history) entsprach nicht den erwartungen"
        self.assertEquals(
            self.console.edit.edit_text, 'foo', failmsg)

        # Zweite Mülleingabe
        self.console.edit.edit_text = 'baa'
        self.console.process_input()
        failmsg = "02 Eingabezeile wurde nach dem letzten Kommando nicht geleert"
        self.assertEquals(
            self.console.edit.edit_text, '', failmsg)
        self.console.com_history_up()
        failmsg = "03 History-Resultat entsprach nicht den erwartungen"
        self.assertEquals(
            self.console.edit.edit_text, 'baa', failmsg)
        self.console.com_history_up()
        failmsg = "04 History-Resultat entsprach nicht den erwartungen"
        self.assertEquals(
            self.console.edit.edit_text, 'foo', failmsg)
        self.console.com_history_down()
        failmsg = "05 History-Resultat entsprach nicht den erwartungen"
        self.assertEquals(
            self.console.edit.edit_text, 'baa', failmsg)
        self.console.com_history_down()
        failmsg = "06 History-Resultat entsprach nicht den erwartungen"
        self.assertEquals(
            self.console.edit.edit_text, '', failmsg)

    def testAutocomplete(self):
        self.console.edit.edit_text = 'loa'
        self.console.autocomplete()
        failmsg = "Autocomplete loa should result in load"
        self.assertEquals(self.console.edit.edit_text, "load ", failmsg)


class TestListSelect(unittest.TestCase):
    def setUp(self):
        #self.handler = logging.StreamHandler()
        #bbutil.ilog.addHandler(self.handler)
        self.test_list = ['a', 'b', 'c', 'd', 'e', 'f']

    def tearDown(self):
        pass

    def testSingleComplexSelector(self):
        intended_list = ['a', 'b', 'c']
        out_list = bbutil.list_select(self.test_list, '1-3')
        reason = "Did not expect %s as a result for the selector '1-3'"
        self.assertEquals(out_list, intended_list, reason % out_list)

        intended_list = ['c', 'd', 'e']
        out_list = bbutil.list_select(self.test_list, '3-5')
        reason = "Did not expect %s as a result for the selector '3-5'"
        self.assertEquals(out_list, intended_list, reason % out_list)

    def testWronglyOrderedComplexSelector(self):
        intended_list = []
        out_list = bbutil.list_select(self.test_list, '5-1')
        reason = "Did expect a failure and not %s as a result for the selector '5-1'"
        self.assertEquals(out_list, intended_list, reason % out_list)

    def testOutOfBoundsComplexSelector(self):
        intended_list = []
        out_list = bbutil.list_select(self.test_list, '1-7')
        reason = "Did expect a failure and not %s as a result for the selector '1-7'"
        self.assertEquals(out_list, intended_list, reason % out_list)

    def testMixedSelectors(self):
        intended_list = ['a', 'c', 'd', 'f']
        out_list = bbutil.list_select(self.test_list, '1,3-4,6')
        reason = "Did not not expect %s as a result for the selector '1,3-4,6'"
        self.assertEquals(out_list, intended_list, reason % out_list)

    def testOneElementComplexSelector(self):
        intended_list = ['d']
        out_list = bbutil.list_select(self.test_list, '4-4')
        reason = "Did not not expect %s as a result for the selector '4-4'"
        self.assertEquals(out_list, intended_list, reason % out_list)

    def testFaultySelector(self):
        intended_list = []
        out_list = bbutil.list_select(self.test_list, 'x-y')
        reason = "Did expect a failure and not %s as a result for the selector 'x-y'"
        self.assertEquals(out_list, intended_list, reason % out_list)

if __name__ == '__main__':
    unittest.main(failfast=False)
