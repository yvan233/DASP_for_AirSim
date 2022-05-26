# 自动控制demo
import time
import socket
from DaspCarClient import DaspCarClient,get_lidar
from threading import Thread

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    remote_ip = host
    
    # 初始化客户端实例,与服务器端建立连接
    client = DaspCarClient(host,port=5001)

    # 订阅雷达流
    thread = Thread(target=get_lidar, args=(remote_ip, 6002,))
    thread.daemon = True
    thread.start()    

    # 开始记录数据
    print("start upload")
    parameter = {"type": "lidar","IP": remote_ip,"port": 6002}
    client.start_upload(parameter)
    client.close()
    thread.join() 