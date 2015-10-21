set_source_files_properties(
    capture.pyx robotvision.pyx binariser.pyx simple_vectorizer.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

# Ornder für Biblioteken
link_directories(${Boost_LIBRARY_DIRS})

# Includes
include_directories(.)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${Eigen_INCLUDE_DIRS})

# Modul für den Zugriff auf die Kamera
cython_add_module(capture capture.pyx capture.cpp buffer.cpp controller.cpp)

cython_add_module(robotvision robotvision.pyx
    )

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pedantic -DNPRINT_DEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O1")

add_library(vision STATIC robotvision.cpp pointcloud.cpp simple_vectorizer.cpp
                            fitcircle.cpp)

set_target_properties(vision PROPERTIES COMPILE_FLAGS -fPIC
                        LINK_FLAGS -fPIC)

# Module linken
target_link_libraries(vision debug-common nabo)
target_link_libraries(capture debug-common)
target_link_libraries(robotvision vision debug-common)

install(
    TARGETS capture robotvision
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/vision
)

if(ENABLE_GTESTS)
    add_subdirectory(test)
endif(ENABLE_GTESTS)
