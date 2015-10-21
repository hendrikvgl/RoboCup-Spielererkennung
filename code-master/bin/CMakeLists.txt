# Ordner für Biblioteken bereitstellen
link_directories(${OpenCV_LIBRARY_DIRS})

# Incudes festlegen
include_directories(.)
include_directories(${OpenCV_INCLUDE_DIRS})


# Skripte installieren
install(
    PROGRAMS  motion masscenter simulation vision visualization walk webdarwin record facedetect
         dummy-debug replay-debug
         color off dancepad motorsetter
         record-audio-data.py start-talking.py demomode.py relay-debug
         motorsetter motor_register_reader mousecontrol.py
         debug-parse motors motor_offseter find_test_failures
         start-service-audio
         logitechcontroller update-env.sh speaker-helper-server speaker-helper
         simplify-config remoteControl.py
    DESTINATION bin
)

# Startskripte für Fieldie, Goalie, PenaltyKick/Goalie and ThrowIn
install(
    PROGRAMS start-demo flash bootup boot-motion.sh
            boot-behaviour.sh start-behaviour start-element start-behaviour-dummy start-ceiling-cam-tracker
    DESTINATION bin
)
