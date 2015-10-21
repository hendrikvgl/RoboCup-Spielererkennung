#!/bin/sh
while 
  true
do
  git log --pretty=format:user:%aN%n%ct --reverse --raw --encoding=UTF-8 --since="2013-04-20" --until="2013-04-29"> /tmp/gource.log
  gource --load-config robocup.gource /tmp/gource.log
done

