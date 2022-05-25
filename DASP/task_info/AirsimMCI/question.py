import socket
from .DaspCarServer import DaspCarServer
import subprocess 

def taskFunction(self,id,adjDirection,datalist):
    type = datalist["Type"]
    name = datalist["Name"]
    # Car
    if type == "Car":
        pass
    # Tank agent
    elif type == "Tank":
        subprocess.Popen(["python",'-u','./MCI/3_send_test_tank.py'],shell=False).wait()
    # UE agent
    elif type == "UE":
        pass
    else:
        pass
    return 0