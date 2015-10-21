# Ordner für Biblioteken bereitstellen
link_directories(${Boost_LIBRARY_DIRS})

# Incudes festlegen
include_directories(.)
include_directories(bitbots/debug)
include_directories(bitbots/lowlevel)
include_directories(bitbots/robot)
include_directories(bitbots/ipc)
include_directories(bitbots/motion)
include_directories(bitbots/util)
include_directories(mitecom)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${Eigen_INCLUDE_DIRS})

# Unterordner verarbeiten
add_subdirectory(nabo)
add_subdirectory(bitbots)
add_subdirectory(mitecom)

# Den reinen PythonCode installieren
EXECUTE_PROCESS(COMMAND ${CMAKE_INSTALL_PREFIX}/bin/debug-parse
		${PROJECT_SOURCE_DIR}/lib
		${CMAKE_INSTALL_PREFIX}/${PYLIB_INSTALL_PATH}
		-r -d ${DEBUG_LEVEL})

