# Den reinen Python-Code installieren
install(DIRECTORY hook_clients hook_system
    DESTINATION ${PYLIB_INSTALL_PATH}
    FILES_MATCHING PATTERN *.py
)

