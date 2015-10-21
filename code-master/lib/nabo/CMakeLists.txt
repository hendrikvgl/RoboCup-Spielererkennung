find_package(Eigen REQUIRED)
find_package(Boost REQUIRED)

include_directories(${Boost_INCLUDE_DIRS})
include_directories(${Eigen_INCLUDE_DIRS})

add_library(nabo STATIC
    kdtree_cpu.cpp
    kdtree_opencl.cpp nabo.cpp
)

set_target_properties(nabo PROPERTIES
    COMPILE_FLAGS -fPIC
    LINK_FLAGS -fPIC
)

install(
    TARGETS nabo
    DESTINATION ${PYLIB_INSTALL_PATH}/nabo
)
