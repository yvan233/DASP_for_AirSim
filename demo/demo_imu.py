# 自动控制demo
import time
import socket
from DaspCarClient import DaspCarClient
from threading import Thread
import cv2
import socket
import json
import time
import numpy as np
import struct
import traceback
from threading import Thread

def get_imu(host = "127.0.0.1", port = 5002):
    """
    长连接循环接收数据框架
    """
    headerSize = 16
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(10) #接收的连接数
        conn, addr = server.accept()
        print('Connected by {}:{}'.format(addr[0], addr[1]))
        # FIFO消息队列
        dataBuffer = bytes()
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                except Exception as e:
                    # 发送端进程被杀掉
                    break
                if data == b"":
                    # 发送端close()
                    break
                if data:
                    # 把数据存入缓冲区，类似于push数据
                    dataBuffer += data
                    while True:
                        if len(dataBuffer) < headerSize:
                            break  #数据包小于消息头部长度，跳出小循环
                        # 读取包头
                        headPack = struct.unpack("!IIQ", dataBuffer[:headerSize])
                        bodySize = headPack[1]
                        if len(dataBuffer) < headerSize+bodySize :
                            break  #数据包不完整，跳出小循环
                        # 读取消息正文的内容
                        body = dataBuffer[headerSize:headerSize+bodySize]
                        # 数据处理
                        thread = Thread(target=MessageHandle, args=(headPack, body, conn,))
                        # 设置成守护线程
                        thread.setDaemon(True)
                        thread.start()    
            
                        # 数据出列
                        dataBuffer = dataBuffer[headerSize+bodySize:]

def MessageHandle(headPack, body, conn):
    if headPack[0] == 1:
        body = json.loads(body.decode())
        print (body["timestamp"])

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    remote_ip = host
    
    # 初始化客户端实例,与服务器端建立连接
    client = DaspCarClient(host)

    # 订阅雷达流
    thread = Thread(target=get_imu, args=(remote_ip, 6003,))
    thread.daemon = True
    thread.start()    

    # 开始记录数据
    print("start upload")
    parameter = {"type": "imu","IP": remote_ip,"port": 6003}
    client.start_upload(parameter)
    client.close()
    thread.join() 