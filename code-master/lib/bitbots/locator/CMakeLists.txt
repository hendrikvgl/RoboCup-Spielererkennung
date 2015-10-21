set_source_files_properties(
    transformer.pyx locator.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

# 19.04.2014 @Robert
# Den Locator aus dem Build entfernt, da er nicht benutzt wird und mir Compilezeit kostet

# Includes
include_directories(.)
include_directories(${Eigen_INCLUDE_DIRS})

# Modul für die Bildpunktetransformation
add_library(transformation STATIC image_point_to_location_transformer.cpp)
set_target_properties(transformation PROPERTIES COMPILE_FLAGS -fPIC LINK_FLAGS -fPIC)
target_link_libraries(transformation robot debug-common)

cython_add_module(transformer transformer.pyx)
target_link_libraries(transformer transformation)

set(INSTALL_TARGETS transformer)

#if(BUILD_LOCATOR)
    # Modul für die Roboterlokalisation
    cython_add_module(locator locator.pyx locator.cpp line_matcher.cpp
                ../robot/kinematic_robot.cpp line_sampler.cpp
                noop_position_filter.cpp ../vision/sample.hpp)

    target_link_libraries(locator debug-common)

    set(INSTALL_TARGETS ${INSTALL_TARGETS} locator)
#endif(BUILD_LOCATOR)

# Module linken
target_link_libraries(transformer debug-common)

#Module installieren
install(
    TARGETS ${INSTALL_TARGETS}
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/locator
)

if(ENABLE_GTESTS)
    add_subdirectory(test)
endif(ENABLE_GTESTS)
