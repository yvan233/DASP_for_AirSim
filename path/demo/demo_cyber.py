# 自动控制demo
import time
import socket
from DaspCarClient import DaspCarClient,get_lidar
from threading import Thread

if __name__ == '__main__':
    host = "192.168.1.4"
    remote_ip = "0.0.0.0"
    # 初始化客户端实例,与服务器端建立连接
    client = DaspCarClient(host)

    # 获取车辆状态
    state = client.get_state()
    print("state",state)  

    # 订阅雷达流
    thread = Thread(target=get_lidar, args=(remote_ip, 5002,))
    thread.daemon = True
    thread.start()    

    # 开始记录数据
    print("start upload")
    parameter = {"type": "lidar","IP": host,"port": 5002}
    client.start_upload(parameter)

    thread.join() 