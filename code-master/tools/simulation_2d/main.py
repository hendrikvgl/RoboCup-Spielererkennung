"""
    To use this System you will need to make several things:
    1. Find debug_intern.hpp and comment in
        //static std::string HOSTNAME(getenv("HOSTNAME"));
        comment out the other line above that (read comments)
    2. Compile
    3. Start This Main and the Supervisor Client
    4. Now Run Start-Behaviour-Dummy with the arguments you like to have
        PLAYER - The Palyer Number
        DP_PORT, DP_HOST - In General localhost and 55556 - Data where the WorldService is running
        MITECOM - The Mitcom PORT - use this like 12[PLAYERNUMBER]21
    5. You shoudl see black dots for robot in the View
    6. Type into Supervisor Client 'start True'
    7. There you go
"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from WorldService import WorldService



if __name__ == '__main__':
    w = WorldService()
    #w.register_robot("Tamara")
    #robot = w.robots["Tamara"]
    #robot.orientation = 45
    #robot.xy = [0, 0]
    #w.update_walking_for("Tamara", 0, -4, 0, 0)

    server = SimpleXMLRPCServer(("localhost",  55556))
    print "Listening on port 55556..."
    server.register_instance(w)
    server.logRequests = False
    w.start_main_loop()
    server.serve_forever()












