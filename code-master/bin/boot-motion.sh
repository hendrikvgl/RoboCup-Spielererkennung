#!/bin/bash

function kill_relevant_python(){
    # Alle noch laufenden Python-Behaviour-Prozesse killen
    for SIGNAL in TERM TERM TERM KILL KILL ; do
        # Searching for our behaviours to be killed: Python processes containing
        # "behaviour" or "start-" or "vision". Then filter out our searching-process
        # and possible gdb processes #2635. Finally extracting the PID's using sed
        PROCESSES=$(ps aux | grep python | grep -e "behaviour" -e "start-" -e "vision" | grep -v -e "PROCESSES" -e "gdb *\-args" | sed -r "s/^[^ ]* *([0-9]*).*/\1/")
        if ! kill -$SIGNAL $PROCESSES python 2> /dev/null ; then
            break
        fi

        sleep 0.2
    done
}

while true ; do
    (
        . /home/darwin/darwin/share/bitbots/boot-defaults.sh

        if $SOFT_MOTION ; then
            # Virtualenv aktivieren
            deactivate 2> /dev/null
            . $BOOT_VIRTUALENV/bin/activate

            kill_relevant_python

            # Wenn möglich, das DarwinIPC aufräumen
            rm -f /dev/shm/DarwinIPC

            speaker-helper "Starting soft motion"
            echo $1 $2
            motion --softoff --softstart --starttest $@
        elif $BOOT_ENABLED ; then
            # Virtualenv aktivieren
            deactivate 2> /dev/null
            . $BOOT_VIRTUALENV/bin/activate

            kill_relevant_python

            # Wenn möglich, das DarwinIPC aufräumen
            rm -f /dev/shm/DarwinIPC

            speaker-helper "Starting motion"
            motion --no --starttest $@
        fi
    )
    echo "You have two seconds to kill this script."
    sleep 2 || exit $?
done

