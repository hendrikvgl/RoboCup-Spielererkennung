#! /bin/bash

RETURNCODE=0

#The ROOT is the file location, the tests directory from gitroot
ROOT=$(readlink -f $(dirname $0))
cd $ROOT/../
#Changing the ROOT to the gitroot
ROOT=`pwd`
#activate VIRTUAL_ENV
if [ -z "$VIRTUAL_ENV" ]
then
    . $ROOT/.py-env/bin/activate 2>/dev/null
fi

FAILED_TASKS=""

for TEST in $(find $ROOT/lib/ -name "test_*.x")
do
    DIR=$(dirname $TEST)
    echo "Test in $DIR gefunden: $(basename $TEST)"
    cd $DIR
    $TEST
    CODE=$?
    if [ $CODE -ne 0 ]
    then
        if [ $CODE -gt $RETURNCODE ]
        then
            RETURNCODE=$CODE
        fi
        if [ $CODE -ne 127 ]
        then
            #Bei exitcode 127 ist der test wegen Architekturproblemen nicht ausführbar
            FAILED_TASKS="$FAILED_TASKS $TEST"
        else
            rm -v $TEST
        fi
    fi
    cd $ROOT
done

if ! [ -z "$FAILED_TASKS" ]
then
    red='\e[0;31m'
    NC='\e[0m' # No Color
    bold=`tput bold`
    normal=`tput sgr0`
    echo -e "${red}${bold}The following tests failed: $FAILED_TASKS${NC}${normal}" 1>&2
fi
echo "Finished running $(find $ROOT/lib/ -name 'test_*.x' | wc -w ) Tests"
echo "$( wc -w <<< ${FAILED_TASKS}) failed"
exit $RETURNCODE
