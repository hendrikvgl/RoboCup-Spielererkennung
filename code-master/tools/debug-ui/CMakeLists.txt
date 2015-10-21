add_subdirectory(lib)
# Skripte installieren
install(
    PROGRAMS bin/debug-ui
    DESTINATION bin
)

# den share-Ordner installieren
#install(DIRECTORY share/ DESTINATION share)

