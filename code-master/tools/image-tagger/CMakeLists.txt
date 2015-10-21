if(JAVA_COMPILE)
    # Hier müssen alle Java-Dateien angegeben werden
    set(SOURCE src/de/bitbots/tagger/startup/Startup.java)
    
    add_custom_target(ImageTagger.classes
        COMMAND ${JAVA_COMPILE} -d ${CMAKE_CURRENT_BINARY_DIR}
                                -classpath src:${CMAKE_CURRENT_BINARY_DIR}
                                ${SOURCE}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        SOURCES ${SOURCE}
        COMMENT "Compiling java files to class files"
    )
    
    add_custom_target(ImageTagger.jar ALL
        COMMAND ${JAVA_ARCHIVE} cfm ImageTagger.jar ${CMAKE_CURRENT_SOURCE_DIR}/Manifest
                                de/bitbots/tagger/*/*.class
                                de/bitbots/tagger/*/*/*.class
                                org/json/*.class
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        DEPENDS ImageTagger.classes
        SOURCES Manifest
        COMMENT "Building jar package"
    )
    
    install(
        FILES ${CMAKE_CURRENT_BINARY_DIR}/ImageTagger.jar
        DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/
    )
    
    install(
        PROGRAMS bin/image-tagger bin/trainer cumulate_color_masqs.py
        DESTINATION bin
    )
else()
    MESSAGE("Kein Java, überspringe ImageTagger")
endif()

