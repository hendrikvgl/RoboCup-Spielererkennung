option(ENABLE_IMAGETAGGER "Heyes ImageTagger bauen" ON)
option(ENABLE_GLROBOT "OpenGL Robot Interface bauen" ON)
option(ENABLE_DEBUGUI "Debug-ui bauen" OFF)
option(ENABLE_DEBUGUINEU "Neue Debug-ui bauen" ON)
option(ENABLE_DEBUGUIHOOK "Neues Debug-UI Hook System bauen" ON)
option(ENABLE_DXL_MONITOR "Den dxl_monitor für den Darwin Mitbauen" ON)
option(ENABLE_FIRMWARE_INSTALLER "Den firmware_installer mitbauen" OFF)
option(ENABLE_IMAGETAGGER_2 "ImageTagger v2 bauen" OFF)

if(ENABLE_IMAGETAGGER)
    add_subdirectory(image-tagger)
endif()

if(ENABLE_GLROBOT AND NOT(ARM_PROCESSOR) AND "${CMAKE_BUILD_TYPE}" STREQUAL "Release")
    add_subdirectory(glrobot)
endif()

if(ENABLE_DEBUGUI)
    add_subdirectory(debug-ui)
endif()

if(ENABLE_DEBUGUINEU)
    add_subdirectory(debug-ui-neu)
endif()

if(ENABLE_DEBUGUIHOOK)
    add_subdirectory(debug-ui-hookable)
endif()

if(ENABLE_IMAGETAGGER_2)
    add_subdirectory(image-tagger-2)
endif()

add_subdirectory(motor-setup)
