
# Motion und Verhalten automatisch Starten
BOOT_ENABLED=true

# Wenn nicht BOOT_ENABLED gesetzt ist, starte automatisch
# eine Motion im Soft_off Modus
SOFT_MOTION=true

# Pfad wo das VirtualEnv installiert st
BOOT_VIRTUALENV=/home/darwin/darwin

# Wenn gesetzt wird kein debug log auf die platte geschrieben
export NO_LOG=1

declare -A BEHAVIOUR_LIST
BEHAVIOUR_LIST[demo]=demo
BEHAVIOUR_LIST[goalie]="behaviour Goalie"
BEHAVIOUR_LIST[fieldie]="behaviour Fieldie"
BEHAVIOUR_LIST[striker]="behaviour Striker"
BEHAVIOUR_LIST[defender]="behaviour Defender"
BEHAVIOUR_LIST[supporter]="behaviour Supporter"
BEHAVIOUR_LIST[teamplayer]="behaviour TeamPlayer"

# Array mit den Typen der Roboter
# Folgende Werte sind möglich:
# demo
# "behaviour Goalie"
# "behaviour TeamPlayer"
# "behaviour Defender"
# "behaviour Striker"
# "behaviour Supporter" (erzwungenes stehenbleiben in Ballnähe)
declare -A PLAYER_BEHAVIOUR
PLAYER_BEHAVIOUR[glados]=demo
PLAYER_BEHAVIOUR[wheatly]=demo
PLAYER_BEHAVIOUR[atlas]=demo
PLAYER_BEHAVIOUR[tamara]=demo
PLAYER_BEHAVIOUR[wilma]=demo
PLAYER_BEHAVIOUR[fiona]=demo
PLAYER_BEHAVIOUR[goal]=demo
PLAYER_BEHAVIOUR[gareth]=demo
PLAYER_BEHAVIOUR[oberon]=demo
PLAYER_BEHAVIOUR[nimue]=demo
PLAYER_BEHAVIOUR[demo]=demo

# simrobots
# testbots für infrastruktur
PLAYER_BEHAVIOUR[simrobot01]=fieldie
PLAYER_BEHAVIOUR[simrobot02]=fieldie
# simbots
PLAYER_BEHAVIOUR[simrobot02]=fieldie
PLAYER_BEHAVIOUR[simrobot03]=fieldie
PLAYER_BEHAVIOUR[simrobot04]=fieldie
PLAYER_BEHAVIOUR[simrobot05]=goalie
PLAYER_BEHAVIOUR[simrobot06]=fieldie
PLAYER_BEHAVIOUR[simrobot07]=fieldie
PLAYER_BEHAVIOUR[simrobot08]=fieldie
PLAYER_BEHAVIOUR[simrobot09]=goalie
PLAYER_BEHAVIOUR[simrobot10]=fieldie
PLAYER_BEHAVIOUR[simrobot11]=fieldie
PLAYER_BEHAVIOUR[simrobot12]=fieldie
PLAYER_BEHAVIOUR[simrobot13]=goalie
PLAYER_BEHAVIOUR[simrobot14]=fieldie
PLAYER_BEHAVIOUR[simrobot15]=fieldie
PLAYER_BEHAVIOUR[simrobot16]=fieldie
PLAYER_BEHAVIOUR[simrobot17]=goalie
PLAYER_BEHAVIOUR[simrobot18]=fieldie
PLAYER_BEHAVIOUR[simrobot19]=fieldie


# Umgebungsvariablen
export DEBUG=1
export VISION_DEBUG=0
export DEBUG_LEVEL=3

export DEBUG_HOST=10.1.1.1

#Auskommentieren um python -O laufen zu lassen. Diese Option wird nur von boot-behaviour beachtet.
#export DEBUGOPT
