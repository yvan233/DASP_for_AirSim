import socket
from .DaspCarServer import DaspCarServer

def taskFunction(self,id,adjDirection,datalist):
    type = datalist["Type"]
    name = datalist["Name"]
    # Car
    if type == "Car":
        pass
    # UE agent
    elif type == "UE":
        UE_ip = datalist["Ip"]
        host = socket.gethostbyname(socket.gethostname())
        remote_ip = host
        server = DaspCarServer(host, port = 5001, UE_ip = UE_ip, vehicle_name = name, remote_ip = remote_ip)
        server.run()
    else:
        pass
    return 0