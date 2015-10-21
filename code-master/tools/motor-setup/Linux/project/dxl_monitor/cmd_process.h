#ifndef _DXL_MONITOR_CMD_PROCESS_H_
#define _DXL_MONITOR_CMD_PROCESS_H_


#include "LinuxDARwIn.h"


void Prompt(int id);
void Help();
void Scan(Robotis::Robot::CM730 *cm730);
void Dump(Robotis::Robot::CM730 *cm730, int id);
void Reset(Robotis::Robot::CM730 *cm730, int id);
void Write(Robotis::Robot::CM730 *cm730, int id, int addr, int value);

#endif
