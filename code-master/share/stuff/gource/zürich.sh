#!/bin/sh
while 
  true
do
  git log --pretty=format:user:%aN%n%ct --reverse --raw --encoding=UTF-8 --since="2013-03-05" --until="2013-03-12"> /tmp/gource.log
  gource --load-config robocup.gource /tmp/gource.log
done

