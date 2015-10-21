add_subdirectory(glrobot)

# Den reinen Python-Code installieren
install(DIRECTORY glrobot
    DESTINATION ${PYLIB_INSTALL_PATH}
    FILES_MATCHING PATTERN *.py
)

