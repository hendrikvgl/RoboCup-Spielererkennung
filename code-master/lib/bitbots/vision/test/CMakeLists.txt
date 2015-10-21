cmake_minimum_required(VERSION 2.6)

FILE(GLOB TEST_SRC *.cpp)

include_directories(${Eigen_INCLUDE_DIRS})
include_directories(.)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${gtest_c_flags} -pedantic -DNPRINT_DEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -DSKIP_SLEEP")

set(TEST_EXECUTABLES "")
foreach(T ${TEST_SRC})
    string(REGEX REPLACE ".*/" "" T ${T})
    string(REGEX REPLACE ".cpp" "" T ${T})
    add_executable(${T}.x ${T}.cpp)
    target_link_libraries(${T}.x vision)
    target_link_libraries(${T}.x ${gtest_link_flags} bitbots_png)

    add_test(${T} ${T}.x)
    set(TEST_EXECUTABLES ${TEST_EXECUTABLES} ${T}.x)
endforeach()

install(
    TARGETS ${TEST_EXECUTABLES}
    RUNTIME DESTINATION ${PROJECT_SOURCE_DIR}/lib/bitbots/vision/test
)

install(
    TARGETS ${TEST_EXECUTABLES}
    RUNTIME DESTINATION ${TEST_INSTALL_DIR}
)

