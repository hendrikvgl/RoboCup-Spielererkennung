from bitbots.modules.dummy.world_service_client import WorldServiceClient

finished = False

worldServiceclient = WorldServiceClient("localhost", 55556)

def nop(args):
    pass

def start(arg):
    worldServiceclient.set_running(arg)


command_dict = {
    "start": start
}


while not finished:
    command = raw_input("Enter Command: ")
    c, args = command.split(" ")[0], command.split(" ")[1:]
    if c == "terminate":
        finished = True
    else:
        function = command_dict.get(c, nop)
        function(args)
