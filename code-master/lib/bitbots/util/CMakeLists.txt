set_source_files_properties(
    joints.pyx png.pyx pydatavector.pyx kalman.pyx kinematicutil.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

include_directories(.)

cython_add_module(joints joints.pyx)
cython_add_module(kalman kalman.pyx)
cython_add_module(pydatavector pydatavector.pyx)

cython_add_module(kinematicutil kinematicutil.pyx)
cython_add_module(png png.pyx)

set(INSTALL_TARGETS joints png kalman kinematicutil pydatavector)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")

add_library(bitbots_png STATIC png.cpp)
add_library(kinematic_util STATIC kinematic_util.cpp)

target_link_libraries(bitbots_png ${PNG_LIBRARY})

target_link_libraries(png bitbots_png debug-common)

target_link_libraries(kinematic_util robot)
target_link_libraries(kinematicutil kinematic_util)

install(
    TARGETS ${INSTALL_TARGETS}
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/util
)

if(ENABLE_GTESTS)
    add_subdirectory(test)
endif(ENABLE_GTESTS)
