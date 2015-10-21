#!/bin/bash
trap : SIGTERM SIGINT
echo $$

cd `dirname $0`

if [[ $1 == "--xscreensaver" ]]
then
  echo "screensaver-support activated"
  export SDL_WINDOWID=$XSCREENSAVER_WINDOW
fi 

while 
  true
do
  git log --pretty=format:user:%aN%n%ct --reverse --raw --encoding=UTF-8 --since="2014-07-16" --until="2014-07-29"> /tmp/gource.log
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


