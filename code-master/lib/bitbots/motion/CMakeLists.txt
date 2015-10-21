set_source_files_properties(
    basemotionserver.pyx motionserver.pyx simulationmotionserver.pyx
    animation.pyx walking.pyx zmpwalking.pyx accmovementtracker.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

#Don't build Cython Module for Release builds, because it's not used.
#It's defined here to have errors in the original module, because i have a include
#solution for the zmpwalking inside the basemotionserver
if("${CMAKE_BUILD_TYPE}" MATCHES RELEASE OR "${CMAKE_BUILD_TYPE}" MATCHES Release)
    set(COMPILE_MODULES_FOR_DEBUG 0)
else()
    set(COMPILE_MODULES_FOR_DEBUG 1)
endif()

# Module
# Das ist hier so unübersichtlich und doof damit er beim builden die richtigen
# teile mit neubuildet eigendlich brauchen die module nicht immer wieder
# alles, aber noch nicht gefunden wie es sonst geht.... (Nils 20.1.14)
cython_add_module(basemotionserver zmpwalking.pxi zmpwalking-impl.pxi basemotionserver.pyx
                    zmp_walk.cpp zmp_walk_parameter.cpp zmp_team_darwin_kinematics.cpp
                    accmovementtracker.pxi accmovementtracker-impl.pxi)
cython_add_module(motionserver motionserver.pyx)
cython_add_module(simulationmotionserver simulationmotionserver.pyx)
cython_add_module(animation animation.pyx)

if(${COMPILE_MODULES_FOR_DEBUG} MATCHES 1)
    cython_add_module(zmpwalking zmpwalking.pyx zmp_walk.cpp zmp_walk_parameter.cpp
                        zmp_team_darwin_kinematics.cpp)

    set_target_properties(zmpwalking PROPERTIES COMPILE_FLAGS -fPIC
                            LINK_FLAGS -fPIC)
    set(PYTHON_MODULE_zmpwalking_BUILD_SHARED OFF)
    set(INSTALL_TARGETS ${INSTALL_TARGETS} zmpwalking)

    cython_add_module(accmovementtracker accmovementtracker.pyx)

    set_target_properties(accmovementtracker PROPERTIES COMPILE_FLAGS -fPIC
                            LINK_FLAGS -fPIC)
    set(PYTHON_MODULE_accmovementtracker_BUILD_SHARED OFF)
    set(INSTALL_TARGETS ${INSTALL_TARGETS} accmovementtracker)
endif()

set(INSTALL_TARGETS animation basemotionserver motionserver simulationmotionserver)

# Modul linken, wenn notwendig
if(${ZMP} MATCHES 1)
    target_link_libraries(zmpwalking debug-common)
endif()
target_link_libraries(animation debug-common)
target_link_libraries(basemotionserver debug-common)
target_link_libraries(motionserver debug-common)
target_link_libraries(simulationmotionserver debug-common)

# Die kompilierten Module installieren
install(
    TARGETS ${INSTALL_TARGETS}
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/motion
    ARCHIVE DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/motion
)

