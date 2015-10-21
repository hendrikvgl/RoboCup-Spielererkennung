set_source_files_properties(
    ipc.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

include_directories(.)
cython_add_module(ipc ipc.pyx shm.cpp)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
add_library(libipc STATIC shm.cpp)

target_link_libraries(ipc -lrt)
target_link_libraries(libipc -lrt)

install(
    TARGETS ipc
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/ipc
)

if(ENABLE_GTESTS)
    add_subdirectory(test)
endif(ENABLE_GTESTS)