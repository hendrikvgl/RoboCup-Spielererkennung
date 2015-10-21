#!/bin/bash

# Etwas warten, bevor wir ein Verhalten starten
sleep 5

while true ; do
	(
        . /home/darwin/darwin/share/bitbots/boot-defaults.sh 2>&1
	    BEHAVIOUR_ERROR=`. /home/darwin/darwin/share/bitbots/boot-defaults.sh 2>&1`
        if ! [ -z "$BEHAVIOUR_ERROR" ]
        then
            MESSAGE="Looks like there war an error while declaring the boot-behaviour: $BEHAVIOUR_ERROR"
            echo "$MESSAGE" 1>&2
            speaker-helper "$MESSAGE"
            sleep 10
        fi

	    if $BOOT_ENABLED ; then
	        # Virtualenv aktivieren
	        deactivate 2> /dev/null
	        . $BOOT_VIRTUALENV/bin/activate

	        # Das eigentliche Behaviour je nach Roboter starten
	        BEHAVIOUR=${PLAYER_BEHAVIOUR[$HOSTNAME]}
	        speaker-helper "Starting behaviour $BEHAVIOUR"
            if ! [ -z "${BEHAVIOUR_LIST[${BEHAVIOUR}]}" ]
            then
                BEHAVIOUR=${BEHAVIOUR_LIST[$BEHAVIOUR]}
            fi

            #Stelle sicher, dass das gewählte Verhalten existiert, wenn ein Parameter dazugegeben wurde, ignoriere dieses
            if ! [ -e $BOOT_VIRTUALENV/bin/start-`sed -r 's/^([^ ]*).*/\1/' <<< $BEHAVIOUR` ]
            then
                MESSAGE="Behaviour $BEHAVIOUR not found! Did you spell it right?"
                ERROR=1
            fi
            if [ -z "$BEHAVIOUR" ]
            then
                MESSAGE="There is no behaviour for $HOSTNAME in boot-defaults."
                ERROR=1
            fi

            if ! [ -z "$ERROR" ] && [ $ERROR -ne 0 ]
            then
                echo $MESSAGE 1>&2
                speaker-helper "$MESSAGE"
                ERROR=0
                sleep 10
                continue
            fi

	        if $DEBUGOPT ; then
                python $BOOT_VIRTUALENV/bin/start-$BEHAVIOUR $@ #| tee $HOME/$(hostname)-$BEHAVIOUR-"$(date)".log
            else
                echo "Run Python -O"
                python -O $BOOT_VIRTUALENV/bin/start-$BEHAVIOUR $@ #| tee $HOME/$(hostname)-$BEHAVIOUR-"$(date)".log
            fi
	    fi
	)

	echo "You have two seconds to kill this script."
	sleep 2 || exit $?
done

