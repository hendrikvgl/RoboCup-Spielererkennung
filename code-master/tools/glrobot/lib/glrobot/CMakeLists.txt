# OpenGL Scenegraph in Python
include_directories(${OPENGL_INCLUDE_DIR})
cython_add_module(scenegraph scenegraph.pyx)

target_link_libraries(scenegraph ${OPENGL_gl_LIBRARY})

install(
    TARGETS scenegraph
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/glrobot/
)

