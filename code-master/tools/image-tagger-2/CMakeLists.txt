include_directories(Capture)
include_directories(png++)

add_library(capture2 STATIC Capture/Buffer.cpp Capture/Image.cpp
	    Capture/YUYVImage.cpp Capture/Controller.cpp Capture/Capture.cpp)
set_target_properties(capture2 PROPERTIES COMPILE_FLAGS -fPIC LINK_FLAGS -fPIC)
include_directories(${Boost_INCLUDE_DIRS})

add_library(tagging STATIC ConfigFile.cpp)
set_target_properties(capture2 PROPERTIES COMPILE_FLAGS -fPIC LINK_FLAGS -fPIC)

add_executable(image-tagger-2 main.cpp)
target_link_libraries(image-tagger-2 capture2 tagging)

find_package(PNG REQUIRED)
find_package(SFML 2.1 REQUIRED system window graphics)

include_directories(${SFML_INCLUDE_DIR})
target_link_libraries(image-tagger-2 ${SFML_LIBRARIES} yaml-cpp)

include_directories(${PNG_INCLUDE_DIR})
target_link_libraries(image-tagger-2 ${PNG_LIBRARY})

install(
    TARGETS image-tagger-2
    DESTINATION bin)
