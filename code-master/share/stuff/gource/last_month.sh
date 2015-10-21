#!/bin/bash
trap : SIGTERM SIGINT
echo $$

cd `dirname $0`

UPDATE=0
for ARG in $@; do
  if [[ $ARG == "--xscreensaver" ]]
  then
    echo "screensaver-support activated"
    export SDL_WINDOWID=$XSCREENSAVER_WINDOW
  elif [[ $ARG == "--update" ]]
  then
    UPDATE=1
    echo "reload of history enabled"
  fi 
done

if [[ $UPDATE == 1 ]]
# Externe-Loop, Berücksichtigt Änderungen
# Braucht aber auch deutlich länger beim neustart
then
  echo "Starting with external update-loop, to reload history after each run"
  while 
    true
  do
    git log --pretty=format:user:%aN%n%ct --reverse --raw --encoding=UTF-8 --since="last month"> /tmp/gource.log
    gource --load-config robocup.gource /tmp/gource.log &

    # save PID so we can clean up after we are killed
    GOURCE_PID=$!
    echo "Current Gource PID is $GOURCE_PID"

    # wait for gource to terminate
    wait $GOURCE_PID

    # Should we receive SIGTERM or SIGINT wait returns an error code above 128
    if [[ $? -gt 128 ]]
    then
        echo "Received Termination-Signal, exiting and killing gource (PID $GOURCE_PID)"
        kill -s KILL $GOURCE_PID
        exit 0
    fi
  done
# Builtin-Loop, also keine registrierung von änderungen
# Dafür ressourcenärmer und startet sofort neu
else
    echo "Starting with builtin update-loop"
    git log --pretty=format:user:%aN%n%ct --reverse --raw --encoding=UTF-8 --since="last month"> /tmp/gource.log
    gource --load-config robocup_loop.gource /tmp/gource.log &

    GOURCE_PID=$!
    echo "Current Gource PID is $GOURCE_PID"

    # wait for gource to terminate
    wait $GOURCE_PID

    # cleanup hier nicht nötig
fi


