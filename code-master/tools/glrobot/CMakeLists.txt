find_package(OpenGL)
if(${OPENGL_FOUND})
    add_subdirectory(lib)

    # Skripte installieren
    install(
        PROGRAMS bin/glrobot
        DESTINATION bin
    )

    # den share-Ordner installieren
    install(DIRECTORY share/ DESTINATION share)
else()
    message("Kein OpenGL gefunden (installiere libgl1-dev)")
endif()

