#! /bin/bash
FILE="$VIRTUAL_ENV/share/env-version"
if ! [ -e $FILE ]; then
    echo 0 >> $FILE
fi

VERSION=`cat $FILE`

ROOT=$(readlink -f $(dirname $0))

. $ROOT/updates.sh

#handle updates for Virtual env and for chroot
if [ -e /startup.sh ]
then
    i=0
    while ! [ -z "${MESSAGES[$i]}" ]
    do
        if ! [ -z "${UPDATES_CHROOT[$i]}" ]
        then
            UPDATES[$i]=${UPDATES_CHROOT[$i]}
        fi
        i=$(expr $i + 1)
    done
fi

i="$VERSION"

while ! [ -z "${MESSAGES[$i]}" ]; do
    echo ${MESSAGES[$i]}
    echo "The following command will be executed: ${UPDATES[$i]}"
    ${UPDATES[$i]}
    if [ $? -ne 0 ]
    then
        echo "Error installing update for version $i"
        exit 1
    fi
    i=$(expr $i + 1)
    echo "$i" > $FILE
done;
