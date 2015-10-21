#!/bin/sh
while 
  true
do
  git log --pretty=format:user:%aN%n%ct --reverse --raw --encoding=UTF-8 --since="2012-06-16" --until="2012-06-27"> /tmp/gource.log
  gource --load-config robocup.gource /tmp/gource.log
done

