set_source_files_properties(
    debug.pyx debugserver.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

# Ornder für Biblioteken
link_directories(${Boost_LIBRARY_DIRS})
link_directories(${OpenCV_LIBRARY_DIRS})

# Includes
include_directories(.)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${Eigen_INCLUDE_DIRS})
include_directories(${OpenCV_INCLUDE_DIRS})

# Modul fürs Debugging
cython_add_module(debug debug.pyx)
cython_add_module(debugserver debugserver.pyx)

add_library(debug-common SHARED
    debug.cpp debug_net.cpp debug_paint.cpp
)

# Module linken
target_link_libraries(debug-common
    ${Boost_SYSTEM_LIBRARY} ${Boost_IOSTREAMS_LIBRARY} ${Boost_THREAD_LIBRARY} ${Boost_DATE_TIME_LIBRARY}
)

target_link_libraries(debug debug-common)
target_link_libraries(debugserver debug-common)

install(
    TARGETS debug debugserver
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/debug
)

install(
    TARGETS debug-common
    LIBRARY DESTINATION lib
)

