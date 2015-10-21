#!/bin/bash

ROOT=$(readlink -f $(dirname $0))
echo $ROOT
cd $ROOT

if [ $# -gt 0 ] ; then
	BUILD_TYPE=$1
else
	BUILD_TYPE="Debug"
fi
BUILD_DIR=build/${BUILD_TYPE}
echo $BUILD_DIR
echo "mkdir -p ${ROOT}/${BUILD_DIR} 2>/dev/null"
mkdir -p ${ROOT}/${BUILD_DIR} 2>/dev/null
cd ${ROOT}/${BUILD_DIR}
echo " PWD: $(pwd)"
cmake ${ROOT} -Dinstall="${ROOT}/install" "-DCMAKE_BUILD_TYPE=$BUILD_TYPE"
echo "cmake ${ROOT} -Dinstall=\"${ROOT}/install\" \"-DCMAKE_BUILD_TYPE=$BUILD_TYPE\""

make -j4 install
