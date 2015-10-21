#!/usr/bin/env python
#-*- coding:utf-8 -*-

from construct import *

RobotInfo = Struct("robot_info",
                   #define PENALTY_NONE                        0
                   #define PENALTY_HL_KID_BALL_MANIPULATION    1
                   #define PENALTY_HL_KID_PHYSICAL_CONTACT     2
                   #define PENALTY_HL_KID_ILLEGAL_ATTACK       3
                   #define PENALTY_HL_KID_ILLEGAL_DEFENSE      4
                   #define PENALTY_HL_KID_REQUEST_FOR_PICKUP   5
                   #define PENALTY_HL_KID_REQUEST_FOR_SERVICE  6
                   #define PENALTY_HL_KID_REQUEST_FOR_PICKUP_2_SERVICE 7
                   #define PENALTY_MANUAL                      15
                   Byte("penalty"),
                   Byte("secs_till_unpenalised")
)

TeamInfo = Struct("team",
                  Byte("team_number"),
                  Enum(Byte("team_color"),
                       BLUE=0,
                       RED=1
                  ),
                  Byte("score"),
                  Byte("penalty_shot"),  #  penalty shot counter
                  ULInt16("single_shots"),  #  bits represent penalty shot success
                  Bytes("coach_message", 40),
                  Rename("coach", RobotInfo),
                  Array(11, Rename("players", RobotInfo))
)

GameState = Struct("gamedata",
                   Const(Bytes("header", 4), "RGme"),
                   Const(Byte("version"), 8),
                   Byte("packet_number"),
                   Byte("players_per_team"),
                   Enum(Byte("game_state"),
                        STATE_INITIAL=0,
                        #auf startposition gehen
                        STATE_READY=1,
                        #bereithalten
                        STATE_SET=2,
                        #spielen
                        STATE_PLAYING=3,
                        #spiel zu ende
                        STATE_FINISHED=4
                   ),
                   Byte("first_half"),
                   Byte("kick_of_team"),
                   Enum(Byte("secondary_state"),
                        STATE_NORMAL=0,
                        STATE_PENALTYSHOOT=1,
                        STATE_OVERTIME=2,
                        STATE_TIMEOUT=3
                   ),
                   Byte("drop_in_team"),
                   ULInt16("drop_in_time"),
                   SLInt16("seconds_remaining"),  #todo haben
                   ULInt16("secondar_seconds_remaining"),  # todo haben

                   Array(2, Rename("teams", TeamInfo))
)

ReturnData = Struct("returndata",
                    Const(Bytes("header", 4), "RGrt"),
                    Const(Byte("version"), 2),
                    Byte("team"),
                    Byte("player"),
                    Byte("message")
)

