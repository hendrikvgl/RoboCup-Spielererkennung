set_source_files_properties(
    pypose.pyx kinematics.pyx comcalculator.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

include_directories(.)

cython_add_module(pypose pypose.pyx)
cython_add_module(kinematics kinematics.pyx )

set(INSTALL_TARGETS pypose kinematics)

if(BUILD_COM_CALCULATOR)
    cython_add_module(comcalculator comcalculator.pyx com_calculator.cpp
                        kinematic_robot.cpp)
    target_link_libraries(comcalculator debug-common)

    set(INSTALL_TARGETS ${INSTALL_TARGETS} comcalculator)
endif(BUILD_COM_CALCULATOR)

#Set some options for creating the library
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pedantic -DNPRINT_DEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -DNPRINT_DEBUG")

if(${YAMLPATH} MATCHES YAMLPATH-NOTFOUND)
    set(YAML_INCLUDE "")
else()
    set(YAML_INCLUDE load_from_config.cpp)
endif()

#create library, so the tests can link without recompiling the whole module
#add_library(robot SHARED kinematic_robot.cpp kinematic_robot.hpp kinematic_joint.hpp
add_library(robot STATIC kinematic_robot.cpp kinematic_robot.hpp kinematic_joint.hpp
                    kinematic_joint-impl.hpp inverse_computation.hpp kinematic_task.cpp
                    robot.pxi ${YAML_INCLUDE})

set_target_properties(robot PROPERTIES COMPILE_FLAGS "-fPIC"
                        LINK_FLAGS -fPIC)

if(NOT ${YAMLPATH} MATCHES YAMLPATH-NOTFOUND)
    target_link_libraries(robot yaml-cpp)
endif()
target_link_libraries(kinematics robot)

install(
    TARGETS ${INSTALL_TARGETS}
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/robot
)
#install(
#    TARGETS robot
#    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib
#)

if(ENABLE_GTESTS)
    add_subdirectory(test)
endif(ENABLE_GTESTS)
