set_source_files_properties(
    serial.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

include_directories(.)
include_directories(${Boost_INCLUDE_DIRS})

# Modul für die Kommunikation über die serielle Schnittstelle
cython_add_module(serial serial.pyx serial.cpp)

add_subdirectory(controller)

# 'serial' linken
target_link_libraries(serial
    ${Boost_SYSTEM_LIBRARY}
    debug-common
)


install(
    TARGETS serial
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/lowlevel
)

