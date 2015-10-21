include_directories(Framework/include)
include_directories(Linux/include)

add_library(darwin Framework/src/CM730.cpp Linux/build/LinuxCM730.cpp)

if(ENABLE_DXL_MONITOR)
    add_executable(dxl_monitor
        Linux/project/dxl_monitor/main.cpp
        Linux/project/dxl_monitor/cmd_process.cpp
    )

    target_link_libraries(dxl_monitor darwin -pthread)

    install(
        TARGETS dxl_monitor
        RUNTIME DESTINATION bin
    )
endif()

if(ENABLE_FIRMWARE_INSTALLER)
    add_executable(firmware_installer
        Linux/project/firmware_installer/main.cpp
        Linux/project/firmware_installer/hex2bin.cpp
    )

    target_link_libraries(firmware_installer darwin -pthread)

    install(
        TARGETS firmware_installer
        RUNTIME DESTINATION bin
    )

    # Firmware Sachen finden
    file(GLOB FIRMWARE_FILES Linux/project/firmware_installer/*.hex)
    install(
        FILES ${FIRMWARE_FILES}
        DESTINATION share/firmware/
    )
endif()

