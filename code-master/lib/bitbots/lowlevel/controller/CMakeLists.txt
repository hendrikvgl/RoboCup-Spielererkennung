
set_source_files_properties(
    controller.pyx register_tables.pyx converter.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)


# Modul für die LowLevel-Kommunikation mit dem cm730 und mx28
cython_add_module(controller controller.pyx)
cython_add_module(converter converter.pyx)
cython_add_module(register_tables register_tables.pyx)


# Controller linken
target_link_libraries(controller debug-common)



install(
    TARGETS controller converter register_tables
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/lowlevel/controller
)

