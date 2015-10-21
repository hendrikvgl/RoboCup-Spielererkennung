cmake_minimum_required(VERSION 2.8)

option(ENABLE_TESTS "Die Tests aktivieren und installieren" ON)
option(ENABLE_TOOLS "Die Tools aktivieren und installieren" ON)
option(ENABLE_PYFLAKES "Pyflakes zum checken von python code nutzen" ON)

#intel compiler stuff
option(INTEL_CC "Use the Intel compiler." OFF)
option(CLANG "Use the CLANG." OFF)
option(ENABLE_GTESTS "Compile and execute C++ tests with gtest." ON)

set(CMAKE_LIBRARY_ARCHITECTURE "arm-linux-gnueabihf")
if (INTEL_CC)
  find_program(CMAKE_C_COMPILER NAMES icc)
  find_program(CMAKE_CXX_COMPILER NAMES icpc)
  find_program(CMAKE_AR NAMES xiar)
  find_program(CMAKE_LINKER NAMES xild)
  set(MY_CXX_FLAGS "-static-intel ")
  set(MY_DEBUG_CXX_FLAGS "-static-intel ")

  if (CMAKE_C_COMPILER MATCHES CMAKE_C_COMPILER-NOTFOUND OR
      CMAKE_CXX_COMPILER MATCHES CMAKE_CXX_COMPILER-NOTFOUND OR
      CMAKE_AR MATCHES CMAKE_AR-NOTFOUND OR
      CMAKE_LINKER MATCHES CMAKE_LINKER-NOTFOUND)
    message(FATAL_ERROR "Cannot find Intel compiler.  You may need to run `. /opt/intel/bin/compilervars.sh intel64'")
  endif ()
elseif(CLANG)
  set(CMAKE_TOOLCHAIN_PREFIX,"llvm-")
  find_program(CMAKE_C_COMPILER NAMES "clang")
  find_program(CMAKE_CXX_COMPILER NAMES "clang++")
  set(MY_CXX_FLAGS "")
  set(MY_DEBUG_CXX_FLAGS "")
  find_program(CMAKE_AR NAMES llvm-ar)
  #find_program(CMAKE_LINKER NAMES llvm-link)
  find_program(CMAKE_ASM_COMPILER NAMES llvm-as)
  find_program(CMAKE_AS NAMES llvm-as)
  set(CMAKE_C_OUTPUT_EXTENSION ".bc")
  #set(CMAKE_C_FLAGS "-emit-llvm")
  #set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -emit-llvm")
  set(MY_CXX_FLAGS "-emit-llvm")

  if (CMAKE_C_COMPILER MATCHES CMAKE_C_COMPILER-NOTFOUND OR
      CMAKE_CXX_COMPILER MATCHES CMAKE_CXX_COMPILER-NOTFOUND OR
      CMAKE_LINKER MATCHES CMAKE_LINKER-NOTFOUND)
    message("${CMAKE_C_COMPILER} MATCHES CMAKE_C_COMPILER-NOTFOUND")
    message("${CMAKE_CXX_COMPILER} MATCHES CMAKE_CXX_COMPILER-NOTFOUND")
    message("${CMAKE_AR} MATCHES CMAKE_AR-NOTFOUND")
    message("${CMAKE_LINKER} MATCHES CMAKE_LINKER-NOTFOUND")
    message(FATAL_ERROR "Cannot find CLANG compiler")
  endif ()
  set(MY_CXX_FLAGS "-ffast-math -Qunused-arguments -fcolor-diagnostics")
else()
    set(MY_CXX_FLAGS "-ffast-math")
endif()
#end clang stuff

# Projektname
project(Darwin)


# Wir wollen die Dateien unter cmake/* finden, für cython
set(CMAKE_CURRENT_LIST_DIR ${PROJECT_SOURCE_DIR})
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake/)

# Python-Version finden
include(FindPythonInterp)
# Cython danach angeben, sonst vcersionskonflikte
include(UseCython)
include(Png)

# Gucken, ob wir JAVA haben
find_package(Java QUIET COMPONENTS Development)

# Python-Version finden
include(FindPythonInterp)
if(NOT PY_VERSION)
    set(PY_VERSION 2.7)
endif(NOT PY_VERSION)
set(PYLIB_INSTALL_PATH "lib/python${PY_VERSION}")

if(NOT ${CMAKE_INSTALL_PREFIX})
    set(${CMAKE_INSTALL_PREFIX} ${CMAKE_CURRENT_SOURCE_DIR}/.py-env)
endif(NOT ${CMAKE_INSTALL_PREFIX})

#Gtest statisch linken erlauben
set(gtest_link_flags ${CMAKE_INSTALL_PREFIX}/lib/libgtest.a)
set(gtest_c_flags -pthread)
set(TEST_INSTALL_DIR ${PYLIB_INSTALL_PATH}/bitbots/cpp_tests)

# handle debug flags
if(DEBUG_LEVEL)
    set(DEBUG_VAR -DDEBUG_COMPILATION_LEVEL=${DEBUG_LEVEL})
else(DEBUG_LEVEL)
    set(DEBUG_LEVEL 9)
endif(DEBUG_LEVEL)

#handle mitecom architecture error with release build on other processor than atom processor @Robert 10.03.2014
if(ATOM_PROCESSOR)
    set(ARCH "-march=atom")
else(ATOM_PROCESSOR)
    set(ARCH "")
    if(ARM_PROCESSOR)
        set(ARCH "-march=armv7l -mfpu=neon -target arm-linux-gnueabihf -mcpu=cortex-a9 -mfloat-abi=hard ")
        set(ARCH "${ARCH} -I/usr/include/arm-linux-gnueabihf/c++/4.8/")
        set(ARCH "${ARCH} -I/usr/include/arm-linux-gnueabihf/")
        set(ARCH "${ARCH} -I/usr/include/arm-linux-gnueabihf/c++/4.8/bits/")
        set(ARCH "${ARCH} -I/usr/lib/gcc/arm-linux-gnueabihf/4.8/include/")
        set(ARCH "${ARCH} -I/usr/include/c++/4.8/")
        set(ARCH "${ARCH} -gcc-toolchain /usr/")
        set(ARCH "${ARCH} -nostdinc")
        set(ARCH "${ARCH} -nobuiltininc")
        set(ARCH "${ARCH} -nostdinc++")
        #-integrated-as
        #-ccc-print-phases
        #-ccc-print-bindings
        # --save-temps -v
        set(ARCH "${ARCH} -Xclang -internal-isystem/usr/include/c++/4.8/backward")
        set(ARCH "${ARCH} -Xclang -internal-isystem/usr/local/include")
        set(ARCH "${ARCH} -Xclang -internal-isystem/usr/lib/clang/3.5/include")
        set(ARCH "${ARCH} -Xclang -internal-isystem/usr/lib/gcc/arm-linux-gnueabihf/4.8/include")
        set(ARCH "${ARCH} -Xclang -internal-isystem/usr/include/arm-linux-gnueabihf")
        set(ARCH "${ARCH} -Xclang -internal-isystem/usr/include")

    else(ARM_PROCESSOR)
        set(ARCH "${ARCH} -mfpmath=sse -msse3 ")
    endif(ARM_PROCESSOR)
endif(ATOM_PROCESSOR)
#set(ARCH "-march=armv7 -ccc-gcc-name arm-linux-gnueabihf-gcc -mfpu=neon -target arm-linux-gnueabihf -mcpu=cortex-a9 -I/usr/include/arm-linux-gnueabihf -gcc-toolchain /usr/ --save-temps")

set(W_UNUSED " -Wunused-parameter -Wunused-variable -Wall -Wextra")
#elif defined() && defined(__ARM_PCS_VFP) -nostdinc

if(VERBOSE_COMPILE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -v")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -v")
endif(VERBOSE_COMPILE)

# Wir setzen ein paar C++ Compiler-Optionen
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11") #enable c++11 for all build-types

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99  ${ARCH}")

set(MY_CXX_FLAGS "-O4 ${ARCH} -fomit-frame-pointer -fstrict-aliasing ${MY_CXX_FLAGS}")
set(DEFINE_PLACES_FLAGS "-DPROJECT_DIR=${PROJECT_SOURCE_DIR} -DINSTALL_DIR=${CMAKE_INSTALL_PREFIX}")
set(CMAKE_CXX_FLAGS_RELEASE "${MY_CXX_FLAGS} ${CMAKE_CXX_FLAGS_RELEASE} ${DEBUG_VAR}  ${W_UNUSED} ${DEFINE_PLACES_FLAGS} ")
set(CMAKE_CXX_FLAGS_RELEASEWITHDEBINF "${MY_CXX_FLAGS} ${CMAKE_CXX_FLAGS_RELEASEWITHDEBINF} ${W_UNUSED} -O2 -g -ggdb ${DEFINE_PLACES_FLAGS} ")
set(CMAKE_CXX_FLAGS_DEBUG "${MY_DEBUG_CXX_FLAGS} ${CMAKE_CXX_FLAGS_DEBUG} ${W_UNUSED} -g -ggdb ${DEFINE_PLACES_FLAGS} ")

# Notwendige Pakete suchen
find_package(Boost REQUIRED COMPONENTS system thread date_time iostreams)
find_package(Eigen REQUIRED)
# Suche und finde yaml, das hat schon einige Probleme gemacht....
find_path(YAMLPATH yaml.h PATH "/usr/include/yaml-cpp" "/usr/include")
#find_package(OpenCV REQUIRED)

# den /share Ordner
install(DIRECTORY share/ DESTINATION share)

# den /overlay Ordner auch installieren
install(DIRECTORY overlay/ DESTINATION overlay USE_SOURCE_PERMISSIONS)

# in den /bin und /lib Ordner absteigen
add_subdirectory(lib)
add_subdirectory(bin)

if(ENABLE_TOOLS)
    add_subdirectory(tools)
endif()

if(ENABLE_TESTS)
    add_subdirectory(tests)
endif()

if(ENABLE_PYFLAKES)

endif()
