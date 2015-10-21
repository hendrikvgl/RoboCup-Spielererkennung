Remotecontrol
============

Der Roboter kann mithilfe von Mäusen/Gamepads und ähnlichem gesteuert werden. Hierfür gibt es zwei Möglichkeiten:
man steckt ein Device in den Roboter und alles klappt automagisch, wenn es nicht geht kannst du versuchen die udev
(siehe unten) anzupassen oder du guckst dir bitbots/modules/basic/remote_control_module an und fixed das Problem ;)

Die andere Alternative ist es, den Controller an deinem Rechner zu stecken und du führst im chroot/virtualenv
remoteControl.py aus. Hier musst du dann im normallfall ein

sudo chmod 777 /dev/input*

machen.


udev
------

Wenn die udev datei auf dem Roboter noch nicht existiert, lege sie doch bitte an:

/etc/udev/rules.d/50-remoteControl.rules

KERNEL=="mouse?", OWNER="darwin", MODE="600"
KERNEL=="mice", OWNER="darwin", MODE="600"
KERNEL=="event?", OWNER="darwin", MODE="600"
