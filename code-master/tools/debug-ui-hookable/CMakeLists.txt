add_subdirectory(lib)
# Skripte installieren
install(
    PROGRAMS bin/debug-ui-hook-server
    DESTINATION bin
)