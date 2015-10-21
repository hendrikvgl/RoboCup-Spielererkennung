#!/bin/bash

cd $(dirname $0)
ROOT=$(pwd -P)

function crop_animation {
    FILE=$1
    echo $FILE
    #First cut so, that evry number has max two decimal places
    sed -i -r "s/([A-Z][^0-9,.]*)([0-9]+\.[0-9][0-9])[0-9]* *(.) */\1\2\3/g" $FILE
    # round down the numbers correct
    sed -i -r "s/([A-Z][^0-9,.]*)([0-9]+\.[0-9])[0-4]/\1\2/g" $FILE
    for i in {0..8}; do
        # round up the numbers correct
        sed -i -r "s/([A-Z][^0-9,.]*)([0-9]+\.)${i}[5-9]/\1\2$(expr $i + 1)/g" $FILE
        sed -i -r "s/([A-Z][^0-9,.]*[0-9]*)$i\.9[5-9]/\1$(expr $i + 1)\.0/g" $FILE
    done
    #special case with two 9
    sed -i -r "s/([A-Z][^0-9,.]*)99\.9[5-9]/\1100\.0/g" $FILE
}

echo `pwd`
for i in $(find ../share/bitbots/animations -name "*.json") ; do
    crop_animation $i
done



