declare -A UPDATES
declare -A UPDATES_CHROOT
declare -A MESSAGES

# Fehlende Software für das Virtualenv und das chroot hier reinschreiben
# Für jedes Updates eine Beschreibung in MESSAGES hinterlegen.
# Wenn für das chroot und das rechnervirtualenv verschiedene Befehle
# auszuführen sind, dann bitte explizit in UPDATES_CHROOT eintragen, ansonsten
# reicht es die UPDATES zu deklarieren

function install {
    for PROGRAM in $@ ; do
        aptitude --version >/dev/null 2>&1
        if [ 0 -ne $? ] ; then
            # aptitude not installed
            sudo apt-get install ${PROGRAM}
            continue
        fi
        S=$(aptitude search "$PROGRAM" | egrep -e "^i...${PROGRAM} .*")
        if [ -z "$S" ] ; then
            sudo aptitude install ${PROGRAM}
        else
            echo "${PROGRAM} is already installed"
            sleep 2
        fi
    done
}

MESSAGES[0]="Installiere libalsaaudio"
UPDATES[0]="install libasound-dev"
UPDATES_CHROOT[0]="scp bitbots@bit-bots.de:subdomains/data/alsaaudio.so ../darwin/lib/python${PYTHON_VERSION}/site-packages/alsaaudio.so"

MESSAGES[1]="libalsaaudio Teil 2"
UPDATES[1]="pip install pyalsaaudio"
UPDATES_CHROOT[1]="echo 'Empty'Update for chroot'"

MESSAGES[2]="not avaible"
UPDATES[2]=""

MESSAGES[3]="not avaible"
UPDATES[3]=""

MESSAGES[4]="not avaible"
UPDATES[4]=""

MESSAGES[5]="not avaible"

UPDATES[5]=""
MESSAGES[6]="not avaible"
UPDATES[6]=""

MESSAGES[7]="Installiere gobject auf Rechnern"
UPDATES[7]="install python-gobject"
UPDATES_CHROOT[7]="echo 'Update only needed on local machine'"

MESSAGES[8]="Installiere libgtest auf Rechnern"
UPDATES[8]="install libgtest-dev"
UPDATES_CHROOT[8]="echo 'Update only needed on local machine'"

MESSAGES[9]="Installiere libpng um opencv loszuwerden"
UPDATES[9]="install libpng12-dev"
UPDATES_CHROOT[9]="echo 'Please \"install\" libpng manually by copying the headers and libraries into the chroot!!!!'"

MESSAGES[10]="not avaible"
UPDATES[10]=""
MESSAGES[11]="not avaible"
UPDATES[11]=""
MESSAGES[12]="not avaible"
UPDATES[12]=""

MESSAGES[13]="not avaible"
UPDATES[13]=""

MESSAGES[14]="not avaible"
UPDATES[14]=""

MESSAGES[15]="not avaible"
UPDATES[15]=""

MESSAGES[16]="not avaible"
UPDATES[16]=""

MESSAGES[17]="not avaible"
UPDATES[17]=""

MESSAGES[18]="Installiere Evdev"
UPDATES[18]="pip install evdev --upgrade"

MESSAGES[19]="Installiere libyaml-cpp-dev da wir die jetzt auch benutzen"
UPDATES[19]="install libyaml-cpp-dev"
UPDATES_CHROOT[19]="echo 'Bitte manuell als root einlaggen und libyaml-cpp-dev installieren, ansonsten gibt es viel Spaß beim Kompilieren'"
