cmake_minimum_required(VERSION 2.8)

option(CLANG "Use the CLANG." OFF)
option(ENABLE_GTESTS "Compile and execute C++ tests with gtest." ON)

if(CLANG)
  set(CMAKE_TOOLCHAIN_PREFIX,"llvm-")
  find_program(CMAKE_C_COMPILER NAMES clang)
  find_program(CMAKE_CXX_COMPILER NAMES clang++)
  set(MY_CXX_FLAGS "")
  set(MY_DEBUG_CXX_FLAGS "")
  find_program(CMAKE_AR NAMES llvm-ar)
  find_program(CMAKE_ASM_COMPILER NAMES llvm-as)
  find_program(CMAKE_AS NAMES llvm-as)
  set(CMAKE_C_OUTPUT_EXTENSION ".bc")
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

#handle mitecom architecture error with release build on other processor than atom processor @Robert 10.03.2014
if(ATOM_PROCESSOR)
    set(ARCH "-march=atom")
endif(ATOM_PROCESSOR)

set(W_UNUSED " -Wunused-parameter -Wunused-variable -Wall -Wextra")

if(VERBOSE_COMPILE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -v")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -v")
endif(VERBOSE_COMPILE)

# Wir setzen ein paar C++ Compiler-Optionen
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11") #enable c++11 for all build-types

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99  ${ARCH}")

set(MY_CXX_FLAGS "-O4 ${ARCH} -fomit-frame-pointer -fstrict-aliasing ${MY_CXX_FLAGS}")
set(CMAKE_CXX_FLAGS_RELEASE "${MY_CXX_FLAGS} ${CMAKE_CXX_FLAGS_RELEASE} ${DEBUG_VAR}  ${W_UNUSED} ")
set(CMAKE_CXX_FLAGS_RELEASEWITHDEBINF "${MY_CXX_FLAGS} ${CMAKE_CXX_FLAGS_RELEASEWITHDEBINF} ${W_UNUSED} -O2 -g -ggdb ")
set(CMAKE_CXX_FLAGS_DEBUG "${MY_DEBUG_CXX_FLAGS} ${CMAKE_CXX_FLAGS_DEBUG} ${W_UNUSED} -g -ggdb ")

# Notwendige Pakete suchen
#find_package(Boost REQUIRED COMPONENTS system thread date_time iostreams)

include_directories(.)
include_directories(./util)
include_directories(/usr/include/python2.7)


add_library(util STATIC util/img_io.cpp)
set_target_properties(util PROPERTIES COMPILE_FLAGS -fPIC LINK_FLAGS -fPIC)

add_library(ezsift STATIC ezsift.cpp)
set_target_properties(ezsift PROPERTIES COMPILE_FLAGS -fPIC LINK_FLAGS -fPIC)

add_library(pybridge SHARED examples/pybridge.cpp)
set_target_properties(pybridge PROPERTIES COMPILE_FLAGS -fPIC LINK_FLAGS -fPIC)
set_target_properties(pybridge PROPERTIES PREFIX "")


add_executable(extract.x examples/feature_extract.cpp)
add_executable(match.x examples/image_match.cpp)

target_link_libraries(ezsift util)
target_link_libraries(pybridge util ezsift python2.7 boost_python)
target_link_libraries(extract.x util ezsift)
target_link_libraries(match.x util ezsift)

install(TARGETS match.x extract.x pybridge RUNTIME DESTINATION ${install} LIBRARY DESTINATION ${install}/../)
