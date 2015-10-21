"""The record-Script is a Tool to allow the recording and playback of darwin-animations.

To start you have to generate the :py:class:`Mainframe`.

Logging Mechanism
-----------------

This Module utilises two different logging librarys.

* Internally this uses the standard python logging module :mod:`logging`.
  All Messages of informational or above are displayed in the console.
* All Messages of certain levels are additionally sent to the standard Bit-Bots debugging
  :class:`bitbots.debug.Scope`.

.. ditaa::
                    special debug objects
       +-------------------------------------------+
       |                                           |
       |                                           V
    +--+---+ message +-------------+  any   +--------------+
    |Module+-------->|PythonLogging+------->|BitBotsLogging|
    |      |         |             |        |              |
    +------+         +-----+-------+        +------+-------+
                any  |     |                       |
             +-----=-+     |informational          |
             |             |                       |
             V             V                       V
          +-------+   +---------+              +-------+
          |LogFile|   |UIConsole|              |DebugUI|
          |{d}    |   |{io}     |              |{io}   |
          +-------+   +---------+              +-------+

"""
