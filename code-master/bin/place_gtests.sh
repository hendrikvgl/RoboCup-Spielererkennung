#!/bin/bash

GTEST_HEADER_DIR="/usr/include/gtest/gtest.h"
GTEST_SRC_DIR="/usr/src/gtest"
GTEST_TMP_BUILD_DIR="/tmp/gtest_compile_dir"

#Breche ab, wenn die Header nicht existieren
if ! [ -e ${GTEST_HEADER_DIR} ]
then
    exit 1
fi

#Prüfe, ob wir gtest haben
if [ -e ${VIRTUAL_ENV}/lib/libgtest.a ] && [ -e ${VIRTUAL_ENV}/lib/libgtest.so ]
then
    exit 0
fi

#baue gtests
if [ -e $GTEST_SRC_DIR ]
then
    #kopiere die sourcen
    cp -prvi ${GTEST_SRC_DIR} ${GTEST_TMP_BUILD_DIR}
    #erstelle build-dir im tmp
    mkdir -p ${GTEST_TMP_BUILD_DIR}/build
    #Wechsel ins Verzeichnis
    cd ${GTEST_TMP_BUILD_DIR}/build
    #baue
    cmake .. || exit 1
    make gtest || exit 1
    cmake .. -DBUILD_SHARED_LIBS=1|| exit 1
    make gtest || exit 1
    #lege die gtests ins repository
    cp -piv libgtest.so libgtest.a ${VIRTUAL_ENV}/lib  || exit 1
else
    exit 1
fi

exit 0
