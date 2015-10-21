#ifdef MITECOM_EXAMPLE

#include "mitecom-network.h"
#include "mitecom-handler.h"

#include <stdlib.h>
#include <unistd.h>
#include <limits.h>
#include <sys/time.h>

using namespace MiTeCom;

/*------------------------------------------------------------------------------------------------*/

// all team mates (including myself)
MixedTeamMates teamMates;


/*------------------------------------------------------------------------------------------------*/

/**
 ** returns the current time in milliseconds
 **
 ** @return number of milliseconds since epoch (i.e. Jan 1, 1970, 0:00 UTC)
 */

uint64_t getCurrentTime () {
	struct timeval tv;
	gettimeofday(&tv, 0);
	return static_cast<uint64_t>( static_cast<uint64_t>(tv.tv_sec) * 1000 + tv.tv_usec / 1000 );
}


/*------------------------------------------------------------------------------------------------*/

/**
 ** Prints a help text on how to start this application.
 */

void usage(const char* programName) {
	printf("Usage: %s <localport> <remoteport> <robotID> <teamID>\n", programName);
	printf("where\n");
	printf("   localport     The local port number (receiving messages) (>1024).\n");
	printf("   remoteport    The port number to broadcast to (>1024).\n");
	printf("   robotID       ID of this robot (> 0)\n");
	printf("   teamID        The ID of the team this robot belongs to (>0)\n");
}


/*------------------------------------------------------------------------------------------------*/

/**
 ** Processes the data from a team mate.
 */

void process(const MixedTeamMate &mate) {
	/* TODO: ignore messages from myself
		if (mate.robotID == myRobotID)
			return;
	*/

	if (teamMates.find(mate.robotID) == teamMates.end()) {
		printf("Adding robot %d to my list of team mates. Welcome.\n", mate.robotID);
	}

	// add team mate to our map
	teamMates[mate.robotID] = mate;

	// remember the last time (i.e. now) that we heard from this robot
	teamMates[mate.robotID].lastUpdate = getCurrentTime();
}


/*------------------------------------------------------------------------------------------------*/

/**
 ** Application entry point.
 */

int main(int argc, char* argv[]) {
	if (argc != 5) {
		fprintf(stderr, "Invalid number of arguments.\n");
		usage(argv[0]);
		return -1;
	}

	int localport  = atoi(argv[1]);
	int remoteport = atoi(argv[2]);
	int robotID    = atoi(argv[3]);
	int teamID     = atoi(argv[4]);

	int sock = mitecom_open(localport);
	if (sock == -1) {
		return -1;
	}

	uint64_t lastBroadcast = getCurrentTime();
	uint64_t lastReport    = getCurrentTime();

	while (true) {
		const int bufferLength = SHRT_MAX;
		char buffer[bufferLength];

		// receive a message (if available), this call is nonblocking
		ssize_t messageLength = mitecom_receive(sock, buffer, bufferLength);
		if (messageLength > 0) {
			// message received, process it
			MixedTeamMate teamMate = MixedTeamParser::parseIncoming(buffer, messageLength, teamID);
			if (teamMate.robotID != robotID) {
				process(teamMate);
			}
		} else {
			// add some delay
			usleep(100*1000 /* microseconds */);
		}

		// send our information out regularly, and check for expired team mates
		if (lastBroadcast + 500 < getCurrentTime()) {
			MixedTeamMate myInformation;
			myInformation.robotID = robotID; // it is me, ME!!!
			myInformation.data[ROBOT_CURRENT_ROLE]         = ROLE_OTHER;
			myInformation.data[ROBOT_ABSOLUTE_X]           =  mrand48() % SHRT_MAX; // millimeters
			myInformation.data[ROBOT_ABSOLUTE_Y]           =  mrand48() % SHRT_MAX; // millimeters
			myInformation.data[ROBOT_ABSOLUTE_ORIENTATION] =  mrand48() % 360;      // degree
			myInformation.data[ROBOT_ABSOLUTE_BELIEF]      = 0.00001;

			MixedTeamCommMessage *messageDataPtr = NULL;
			uint32_t messageDataLength = 0;

			// serialize and broadcast data
			messageDataPtr = MixedTeamParser::create(&messageDataLength, myInformation, teamID, robotID);
			mitecom_broadcast(sock, remoteport, messageDataPtr, messageDataLength);
			free(messageDataPtr);

			// expire team mates we haven't seen in a while
			for (MixedTeamMates::iterator it = teamMates.begin(); it != teamMates.end(); ) {
				if ((it->second).lastUpdate + 2000 < getCurrentTime()) {
					printf("I didn't hear from %d for a while. Good bye, %d.\n", it->first, it->first);
					teamMates.erase(it++);
				} else
					it++;
			}
		}

		// print a report about the available team mates
		if (lastReport + 2000 < getCurrentTime() && teamMates.size() > 0) {
			printf("=== REPORT ============================================\n");
			for (MixedTeamMates::iterator it = teamMates.begin(); it != teamMates.end(); it++) {
				printf("Team mate %d\n", it->first);
				printf("         Position on field: (%d, %d) at %d degree\n",
						(it->second).data[ROBOT_ABSOLUTE_X],
						(it->second).data[ROBOT_ABSOLUTE_Y],
						(it->second).data[ROBOT_ABSOLUTE_ORIENTATION]);
				printf("   Belief in this position: %.3f\n",
						(it->second).data[ROBOT_ABSOLUTE_BELIEF]/255.);
			}
			lastReport = getCurrentTime();
			printf("\n");
		}
	}

	return 0;
}


#endif
