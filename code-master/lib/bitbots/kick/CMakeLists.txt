set_source_files_properties(
    bezier.pyx kickIPC.pyx phaseIPC.pyx functionWrapper.pyx
    vector.pyx
    PROPERTIES CYTHON_IS_CXX TRUE
)

cython_add_module(functionWrapper functionWrapper.pyx
    )

cython_add_module(vector vector.pyx
    )

cython_add_module(bezier bezier.pyx
    )

cython_add_module(phaseIPC vector.pyx phaseIPC.pyx
    )

cython_add_module(kickIPC bezier.pyx phaseIPC.pyx functionWrapper.pyx
    vector.pyx kickIPC.pyx
    )

# Die kompilierten Module installieren
install(
    TARGETS kickIPC vector bezier functionWrapper phaseIPC
    LIBRARY DESTINATION ${PYLIB_INSTALL_PATH}/bitbots/kick
)

